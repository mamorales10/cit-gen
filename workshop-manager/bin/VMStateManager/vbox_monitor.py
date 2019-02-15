import gc
import logging
import os
import time
import traceback

import gevent.monkey
from gevent.lock import BoundedSemaphore
from virtualbox import Manager
from virtualbox.library import SessionState, MachineState, LockType
from lxml import etree

from manager_constants import LOCK_WAIT_TIME, VBOX_PROBETIME, VM_RESTORE_TIME
from gui_constants import WORKSHOP_CONFIG_DIRECTORY

gevent.monkey.patch_all()

mgr = Manager()
vbox = mgr.get_virtualbox()
session = mgr.get_session()

groupToVms = {}
availableState = []
availableInfo = []
notAvailableState = []
notAvailableInfo = []
restoreState = []
restoreInfo = []
vms = {}

# vars needed for gevent (lock)
queueStateSem = BoundedSemaphore(1)
availableInfoSem = BoundedSemaphore(1)

def getGroupToVms():
    return groupToVms


def getAvailableState():
    return availableState

def getAvailableInfo():
    return availableInfo


####functions needed for testbed manager threads:
def getVMInfo(session, machine):
    answer = {}
    answer["name"] = str(machine.name)
    answer["groups"] = machine.groups
    answer["vrde"] = machine.vrde_server.enabled
    answer["vrdeproperty[TCP/Ports]"] = str(machine.vrde_server.get_vrde_property('TCP/Ports'))
    answer["VMState"] = machine.state

    # need active machine/console for the following:
    if session.state != SessionState(1) or machine.state != MachineState(5):
        logging.debug("session is locked or machine is not running, cannot get console (1)"+str(session.state))
        return answer
    machine.lock_machine(session, LockType(1))
    console = session.console
    if console == None:
        logging.debug("cannot get console (2), machine is probably off")
        session.unlock_machine()
        return answer

    answer["VRDEActiveConnection"] = console.vrde_server_info.active
    res = console.display.get_screen_resolution(0)
    # try to set it to 16 bpp to reduce throughput requirements
    # if res > 16:
    #    logging.debug("Sending hint to adjust resolution")
    #    console.display.setVideoModeHint(0, True, False, 0, 0, 0, 0, 16)
    #    res = console.display.getScreenResolution(0)
    #    logging.debug("After adjustment request"+str(res))
    answer["VideoMode"] = res[2]
    session.unlock_machine()
    return answer


def powerdownMachine(session, machine):
    try:
        if session.state != SessionState(1) or machine.state != MachineState(5):
            logging.debug("session is locked or machine is not running, not powering down")
            return -1
        machine.lock_machine(session, LockType(1))
        console = session.console
        if console != None:
            logging.debug("Calling Power Down API Function")
            progress = console.power_down()
            progress.wait_for_completion(-1)
        else:
            logging.info("can't get console, vm is probably off")
        session.unlock_machine()
        return 0
    except Exception as e:
        logging.error("error during powerdown" + str(e))
        session.unlock_machine()
        return -1


def restoreMachine(session, machine):
    if session.state != SessionState(1) or (machine.state != MachineState(1) and machine.state != MachineState(4)):
        logging.debug("session is locked or machine is not powered off, not restoring vm. Session State:" + str(session.state) + "Machine State:" + str(machine.state))
        return -1
    try:
        machine.lock_machine(session, LockType(1))
        snap = machine.current_snapshot
        # have to reference using session for some weird reason!
        logging.debug("Calling Restore API Function")
        progress = session.machine.restore_snapshot(snap)
        progress.wait_for_completion(-1)
        session.unlock_machine()
        return 0
    except Exception as e:
        logging.error("Error in Restore: " + str(mgr) + " " + str(e))
        traceback.print_exc()
        session.unlock_machine()
        return -1


def startMachine(session, machine):
    try:
        if session.state != SessionState(1) or machine.state != MachineState(2):
            logging.debug( "session is locked, not starting vm")
            return -1
        logging.debug("Calling Launch API Function")
        progress = machine.launch_vm_process(session, "headless", "")
        progress.wait_for_completion(-1)
        session.unlock_machine()
        return 0
    except Exception as e:
        logging.error("error during start" + str(e))
        session.unlock_machine()
        return -1


def makeAvailableToNotAvailable(vmNameList):
    logging.info("making Available to NotAvailable: " + str(vmNameList))
    for vmName in vmNameList:
        queueStateSem.wait()
        queueStateSem.acquire()
        availableState.remove(vmName)
        notAvailableState.append(vmName)
        queueStateSem.release()


def makeNotAvailableToRestoreState(vmNameList):
    logging.info("making NotAvailable to Restore: " + str(vmNameList))
    for vmName in vmNameList:
        queueStateSem.wait()
        queueStateSem.acquire()
        notAvailableState.remove(vmName)
        restoreState.append(vmName)
        queueStateSem.release()


def execShutdownCmds(machine):
    logging.info("execShutdownCmds: machine: " + str(machine.groups))
    try:
        machine_group = machine.groups[0]
        workshopName = str(machine_group.encode('ascii', 'ignore')).split('/')[1]
        xmlFileName = workshopName + ".xml"

        tree = etree.parse(os.path.join(WORKSHOP_CONFIG_DIRECTORY, xmlFileName))
        root = tree.getroot()
        vmset = root.find('testbed-setup').find('vm-set')

        for vm in vmset.findall('vm'):
            currentVM = vm.find('name').text
            if currentVM in machine.name:
                logging.info("execShutdownCmds: Match found! (" + currentVM + " in " + machine.name + ")")
                # Find shutdown commands to be executed
                shutdownCommands = vm.find('shutdown-commands')
                if shutdownCommands is not None:
                    cmds = shutdownCommands.findall('cmd')
                    if len(cmds):  # Shutdown commands found
                        cmds.sort(key=lambda x: x.attrib['seq'])  # Sort shutdown commands by sequence
                        # Iterate through commands and execute them
                        for cmd in cmds:
                            username = cmd.find('username').text.strip()
                            password = cmd.find('password').text.strip()

                            # Create session to the machine
                            machine_session = machine.create_session()
                            guest_session = machine_session.console.guest.create_session(username, password)

                            cmdToExecute = cmd.find('syscall')
                            if cmdToExecute is not None:  # command is a system call
                                cmdToExecute = cmdToExecute.text.strip()
                                guest_session.execute('/bin/bash', ['-c', cmdToExecute])
                            else:
                                cmdToExecute = cmd.find('copyfrom')
                                if cmdToExecute is not None:  # command is a copy from
                                    sourceFile = cmdToExecute.find('source-file').text.strip()
                                    destDir = cmdToExecute.find('dest-dir').text.strip()
                                    guest_session.file_copy_from_guest(sourceFile, destDir, []).wait_for_completion()
                            guest_session.close()
    except Exception:
        logging.info("execShutdownCmds: An error occurred: " + str(machine.groups))


def makeRestoreToAvailableState():  # will look at restore buffer and process any items that exist
    global vms
    global groupToVms
    restoreSubstates = {}
    while True:
        try:
            # Need to reload all vms that are in the group of the vm in the "restore" state
            # get each vm in restoreState list
            for vmToRestore in restoreState:
                # if this vm has a group
                logging.debug("vmToRestore" + str(vmToRestore))
                if vmToRestore in vms and "groups" in vms[vmToRestore]:
                    # get all vms in group
                    groupToRestore = str(vms[vmToRestore]["groups"][0])
                    logging.debug("groupToRestore" + str(groupToRestore))
                    # add each vm in group to restoreSubstate list (if haven't already)
                    for vmInGroup in groupToVms[groupToRestore]:
                        logging.debug("vmInGroup" + str(vmInGroup))
                        if vmInGroup not in restoreSubstates:
                            restoreSubstates[vmInGroup] = "pending"
                            # Process next stage in restore

            logging.debug("Restore substates:"+str(restoreSubstates))
            vmsToRemoveFromQueue = []
            for substate in restoreSubstates:
                logging.debug("Processing state for:"+str(substate)+str(restoreSubstates[substate]))
                queueStateSem.wait()
                queueStateSem.acquire()
                mach = vbox.find_machine(substate)
                vmState = getVMInfo(session, mach)["VMState"]
                queueStateSem.release()
                logging.debug("currState:" + str(vmState))
                result = -1
                if restoreSubstates[substate] == "pending" and vmState == MachineState(5):
                    logging.debug("CALLING POWEROFF"+str(substate)+":"+str(restoreSubstates[substate]))
                    execShutdownCmds(mach)
                    result = powerdownMachine(session, mach)
                    if result != -1:
                        restoreSubstates[substate] = "poweroff_sent"

                elif restoreSubstates[substate] == "poweroff_sent" and vmState == MachineState(1) or vmState == MachineState(4):
                    logging.debug("CALLING RESTORE"+str(substate)+":"+str(restoreSubstates[substate]))
                    result = restoreMachine(session, mach)
                    if result != -1:
                        restoreSubstates[substate] = "restorecurrent_sent"

                elif restoreSubstates[substate] == "restorecurrent_sent" and vmState == MachineState(2):
                    logging.debug("CALLING STARTVM"+str(substate)+":"+str(restoreSubstates[substate]))
                    result = startMachine(session, mach)
                    if result != -1:
                        restoreSubstates[substate] = "startvm_sent"

                elif restoreSubstates[substate] == "startvm_sent" and vmState == MachineState(5):
                    restoreSubstates[substate] = "complete"
                    queueStateSem.wait()
                    queueStateSem.acquire()
                    if substate in restoreState:
                        # remove from restore so it can be added to available buffer once again
                        restoreState.remove(substate)
                    if substate in notAvailableState:
                        notAvailableState.remove(substate)
                    queueStateSem.release()
                    vmsToRemoveFromQueue.append(substate)

            for rem in vmsToRemoveFromQueue:
                if rem in restoreSubstates:
                    del restoreSubstates[rem]
            time.sleep(VM_RESTORE_TIME)
        except Exception as e:
            logging.error("RESTORE: An error occured: "+str(e))
            time.sleep(LOCK_WAIT_TIME)
            pass


def makeNewToAvailableState(vmNameList):
    logging.info("making New to Available: " + str(vmNameList))
    for vmName in vmNameList:
        queueStateSem.wait()
        queueStateSem.acquire()
        availableState.append(vmName)
        queueStateSem.release()


def manageStates():
    global vms
    global groupToVms
    global availableInfo

    while True:
        try:
            logging.debug("Manage States loop start")
            currvms = {}
            currGroupToVms = {}

            # first get all vms
            for mach in vbox.machines:
                logging.debug("getting info for machine"+str(mach.name))
                currvms[str(mach.name)] = getVMInfo(session, mach)

            # for each vm get info and place in state list
            logging.debug("placing info into state list")
            for vm in currvms:
                # get group name and add this vm to a dictionary of that group:
                for group in currvms[vm]["groups"]:
                    gname = str(group)
                    if gname != "/":
                        if gname not in currGroupToVms:
                            currGroupToVms[gname] = []
                        currGroupToVms[gname].append(vm)

                        # so we get all at once (may have to create a lock?)
            queueStateSem.wait()
            queueStateSem.acquire()
            ###lock###
            vms = currvms
            groupToVms = currGroupToVms
            ###unlock###
            queueStateSem.release()

            ########Assign each vm into a state list############

            # first look at any "not available" to see if they go into the "restore" state
            nasList = []
            for vmName in vms:
                if "VRDEActiveConnection" in vms[vmName]:
                    if vms[vmName]["VRDEActiveConnection"] == 1 and vmName in availableState and vmName not in notAvailableState and vmName not in restoreState:
                        nasList.append(vmName)
                    elif vms[vmName]["VRDEActiveConnection"] == 0 and vmName in notAvailableState and vmName not in restoreState and vmName not in restoreState:
                        restoreState.append(vmName)

            makeAvailableToNotAvailable(nasList)
            # Note that the restore thread will move vms in restore buffer available after processing
            # add any newly available vms into the available buffer
            av = []
            for vmName in vms:
                if "vrde" in vms[vmName] and vms[vmName]["vrde"] == 1 and vms[vmName]["VMState"] == MachineState(5):
                    # make available
                    if vmName not in notAvailableState and vmName not in restoreState and vmName not in availableState:
                        av.append(vmName)
            makeNewToAvailableState(av)

            # add available info to available vms
            availableInfoSem.wait()
            availableInfoSem.acquire()
            availableInfo = []
            for vmName in availableState:
                if "name" in vms[vmName] and "vrdeproperty[TCP/Ports]" in vms[vmName]:
                    availableInfo.append((vms[vmName], "Available"))
            for vmName in notAvailableState:
                if "name" in vms[vmName] and "vrdeproperty[TCP/Ports]" in vms[vmName]:
                    availableInfo.append((vms[vmName], "Not available"))
            for vmName in restoreState:
                if "name" in vms[vmName] and "vrdeproperty[TCP/Ports]" in vms[vmName]:
                    availableInfo.append((vms[vmName], "Restoring"))
            availableInfoSem.release()

            # Print out status
            logging.info("\n\n\n")
            logging.info("status:")
            logging.info("available:"+str(availableState))
            logging.info("notAvailable:"+str(notAvailableState))
            logging.info("restore:"+str(restoreState))
            time.sleep(VBOX_PROBETIME)

        except Exception as x:
            logging.error("STATES: An error occurred:" + str(x))
            time.sleep(LOCK_WAIT_TIME)


def unitIsAvailable(vm_set):
    for vm in vm_set:
        if (vm not in availableState and vms[vm]["vrde"]) or (vms[vm]["VMState"] != MachineState(5)):
            return False
    return True


def cleanup():
    global mgr
    global vbox
    global session
    logging.info("Cleaning up VBOX_MONITOR...")
    try:
        logging.info("Removing VirtualBox ISession...")
        del session
        logging.info("Removing IVirtualBox Interface...")
        del vbox
        logging.info("Removing VirtualBox Manager...")
        del mgr
        logging.info("Collecting Garbage...")
        gc.collect()
        logging.info("Clean up complete. Exiting...")

    except Exception as e:
        logging.error("Error during cleanup"+str(e))


if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)

    stateAssignmentThread = gevent.spawn(manageStates)
    restoreThread = gevent.spawn(makeRestoreToAvailableState)

    try:
        gevent.joinall([stateAssignmentThread, restoreThread])
    except Exception as e:
        logging.error("An error occurred in threads"+str(e))
        cleanup()
