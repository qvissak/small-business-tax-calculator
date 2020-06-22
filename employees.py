import csv
import queue
import sys

# federal_filing_status is an enum, valid values are "SINGLE" (single or married filing jointly), "MARRIED" (married filing jointly), or "HEAD_OF_HOUSEHOLD" (head of household)
# state_filing_status is an enum, valid values are "S" (single), "M" (married), "MH" (married but use single rate), or "NRA" (non-resident alien) 

class Employees():
    def __init__(self):
        with open("employees.csv", newline="") as csv_file:
            csv_reader = csv.reader(csv_file, delimiter=',', skipinitialspace=True)
            next(csv_reader) # skip the headers
            employees = queue.Queue()
            for row in csv_reader:
                employees.put(dict(
                    name = row[0],
                    wage = float(row[1]),
                    federal_filing_status = row[2],
                    has_two_jobs = row[3].lower() == "yes",
                    dependents_amount = int(row[4]),
                    other_income = int(row[5]),
                    deductions = int(row[6]),
                    extra_withholding = int(row[7]),
                    state_total_allowances = int(row[8]),
                    state_filing_status = row[9]
                ))
            self.employees = employees

    def __next__(self):
        if self.employees.empty():
            raise StopIteration()
        return self.employees.get()

    def __iter__(self):
        return self

sys.modules[__name__] = Employees()
