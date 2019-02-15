# Queue import
from Queue import Queue


class Workshop_Queue:
    """ A Workshop_Queue encapsulates Workshop Units into a structure that features a Queue.

    Attributes:
        workshopName (str): The name of the workshop.
        materials (list of str): A list of relative paths to materials associated with the workshop.
        q (Queue): A queue that facilitates the distribution of Workshop Units.
    """

    def __init__(self, workshopName, materials):
        """ Constructor for a Workshop object.

        Args:
            workshopName (str): The name of the workshop.
            materials (list of str): A list of relative paths to materials associated with the workshop.
        """
        self.workshopName = workshopName
        self.materials = materials
        self.q = Queue()
