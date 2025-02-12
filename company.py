""" This module is for creating company class
This company class include an employees dictionary that include person object
from database file

"""
##############################################################################

from person import *

##############################################################################

class Company:
    def __init__(self, name, employee_database_file):
        """

        :param name: company name
        :param employee_database_file: employee database
        """

        # company name
        self.name = name

        # set database file variable
        self.employee_database_file = employee_database_file

        # create an empty dic of employee
        self.employees = {}

        # read database file
        self.import_employee_database()

    def import_employee_database(self):
        """
        Read the employee database, clean each record, parse them and create the employee dic

        :return: none
        """

        # read the database and clean whitespace from rach record
        self.read_and_clean_database_record()

        # read each line and parse the employee id_no, first name, and last name
        self.parse_employee_records()

        # create employee dic
        self.create_employee_dic()

    def read_and_clean_database_record(self):
        """
        read and clean database
        :return: none
        """
        try:
            file = open(self.employee_database_file, 'r')
        except FileNotFoundError:
            print(f"Creating databased {self.employee_database_file}")
            file = open(self.employee_database_file, 'w+')

        self.cleaned_records = [cleaned_line for cleaned_line in [line.strip() for line in file.readlines()] if cleaned_line != '']

        file.close()

    def parse_employee_records(self):
        """
        split each line into employee if, first name, and last name
        :return: none
        """
        try:
            self.employee_list = [(int(element[0].strip()), element[1].strip(), element[2].strip()) for element in [line.split(',') for line in self.cleaned_records]]
        except Exception:
            print("Invalid inout file")
            exit()

    def create_employee_dic(self):
        """
        add everyone into the company list
        :return:none
        """

        for employee in self.employee_list:
            try:
                id_number, fname, lname= employee

                new_person = Person(first_name=fname, last_name= lname)

                self.employees[id_number] = new_person

            except Exception:
                print("name is not fully specified")

    def print_employees(self):
        for id, p in self.employees.items():
            print(f"id:{id} first name: {p.first_name} last name: {p.last_name}")
        print()

if __name__ == "__main__":
    company_name = "good"

    employee_file = "./default_employee_database.txt"

    company = Company(company_name, employee_file)

    company.print_employees()










