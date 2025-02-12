"""a module for creating person class"""

class Person:
    def __init__(self, first_name, last_name):
        """

        :param first_name: fist name
        :param last_name:  last name
        """

        self.first_name=first_name
        self.last_name = last_name

    def full_name(self):
        """

        :return: full name of the person
        """

        return self.first_name + " " + self.last_name