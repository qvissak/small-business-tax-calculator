import csv
import employees
import json
import os
import requests
import sys

def create_spreadsheets_if_not_exist(payroll_spreadsheet_filename, ytd_payroll_spreadsheet_filename):
    if not os.path.exists(payroll_spreadsheet_filename):
        with open(payroll_spreadsheet_filename, "w") as file:
            writer = csv.writer(file, quoting=csv.QUOTE_ALL)
            writer.writerow(["Date", "Name", "Hours", "Gross", "Net", "Federal", "SS", "Medicare", "Employer's Contribution", "State"])
    if not os.path.exists(ytd_payroll_spreadsheet_filename):
        with open(ytd_payroll_spreadsheet_filename, "w") as file:
            writer = csv.writer(file, quoting=csv.QUOTE_ALL)
            writer.writerow(["Name", "Earnings YTD"])

def get_hours_from_intuit_csv(filename, employee_name):
    with open(filename, "r") as file:
        csv_reader = csv.reader(file, delimiter=',', skipinitialspace=True)
        next(csv_reader) # skip the title
        next(csv_reader) # skip the newline
        next(csv_reader) # skip the headers
        hours = 0
        for row in csv_reader:
            first_name = row[6]
            last_name = row[7]
            name_list = employee_name.split(" ")
            if first_name == name_list[0] and last_name == name_list[1]:
                hours = row[2]
                break
        return hours

def get_gross_pay_ytd_from_ytd_payroll_spreadsheet(filename, employee_name):
    with open(filename, "r") as file:
        csv_reader = csv.reader(file, delimiter=',', skipinitialspace=True)
        next(csv_reader) # skip the headers
        gross_pay_ytd = 0
        for row in csv_reader:
            name = row[0]
            if name == employee_name:
                gross_pay_ytd = row[1]
                break
        return gross_pay_ytd

def calculate_pay(employee, hours, gross_pay_ytd):
    # source: https://onpay.com/payroll-calculator-tax-rates/oklahoma
    url = "https://calculators.symmetry.com/api/calculators/salary?report=none"
    payload = {
        "grossPayType": "PAY_PER_PERIOD",
        "state": "OK",
        "grossPay": round(hours * employee["wage"], 2),
        "grossPayYTD": round(gross_pay_ytd, 2),
        "payFrequency": "BI_WEEKLY",
        "exemptFederal": "false",
        "exemptFica": "false",
        "exemptMedicare": "false",
        "w42020": "true",
        "federalFilingStatusType2020": employee["federal_filing_status"],
        "federalAllowances": "0",
        "twoJobs2020": employee["has_two_jobs"],
        "dependents2020": employee["dependents_amount"],
        "otherIncome2020": employee["other_income"],
        "deductions2020": employee["deductions"],
        "additionalFederalWithholding": employee["extra_withholding"],
        "roundFederalWithholding": "false",
        "otherIncome": [],
        "rates": [],
        "payCodes": [],
        "stockOptions": [],
        "stateInfo": {
            "parms": [
                {
                    "name": "TOTALALLOWANCES",
                    "value": employee["state_total_allowances"]
                },
                {
                    "name": "stateExemption",
                    "value": "false"
                },
                {
                    "name": "FILINGSTATUS",
                    "value": employee["state_filing_status"]
                },
                {
                    "name": "additionalStateWithholding",
                    "value": "0"
                }
            ]
        },
        "voluntaryDeductions": [],
        "presetDeductions": [],
        "presetImputed": []
    }
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json",
        "pcc-api-key": "286qqx5P7rhR0dttrHeOdZDcEzl5fsxhqsCb9OTS4vUNC9"
    }
    response = requests.post(url, data=json.dumps(payload), headers=headers)
    return response.json()["content"]

def save_pay_to_spreadsheet(filename, date, employee, hours, pay):
    with open(filename, "a") as file:
        writer = csv.writer(file, quoting=csv.QUOTE_ALL)
        writer.writerow([date, employee["name"], hours, pay["grossPay"], pay["netPay"], pay["federal"], pay["fica"], pay["medicare"], round(float(pay["grossPay"]) * 0.0765, 2), pay["state"]])

def update_ytd_spreadsheet(filename, employee_name, pay):
    with open(filename, "r") as file:
        csv_reader = csv.reader(file, delimiter=',', skipinitialspace=True)
        out_file = open("temp.csv", "a")
        writer = csv.writer(out_file, quoting=csv.QUOTE_ALL)
        found = False
        for row in csv_reader:
            if row[0] == employee_name:
                found = True
                ytd_so_far = float(row[1])
                row[1] = round(ytd_so_far + float(pay["grossPay"]), 2)
            writer.writerow(row)
        if not found:
            writer.writerow([employee_name, pay["grossPay"]])
        out_file.close()
    os.remove(filename)
    with open("temp.csv", "r") as file:
        csv_reader = csv.reader(file, delimiter=',', skipinitialspace=True)
        out_file = open(filename, "a")
        writer = csv.writer(out_file, quoting=csv.QUOTE_ALL)
        for row in csv_reader:
            writer.writerow(row)
        out_file.close()
    os.remove("temp.csv")

def main():
    payroll_spreadsheet_filename = "FFF Payroll Spreadsheet.csv"
    ytd_payroll_spreadsheet_filename = "FFF Payroll YTD Spreadsheet.csv"
    create_spreadsheets_if_not_exist(payroll_spreadsheet_filename, ytd_payroll_spreadsheet_filename)

    # command line arguments or prompted input
    date = sys.argv[1] if len(sys.argv) > 1 else input(f"Payroll date (MM/DD/YYYY): ")
    intuit_filename = sys.argv[2] if len(sys.argv) > 2 else input("Intuit filename: ")

    for employee in employees:
        employee_name = employee["name"]
        hours = get_hours_from_intuit_csv(intuit_filename, employee_name)
        gross_pay_ytd = get_gross_pay_ytd_from_ytd_payroll_spreadsheet(ytd_payroll_spreadsheet_filename, employee_name)
        try:
            pay = calculate_pay(employee, float(hours), float(gross_pay_ytd))
            save_pay_to_spreadsheet(payroll_spreadsheet_filename, date, employee, float(hours), pay)
            update_ytd_spreadsheet(ytd_payroll_spreadsheet_filename, employee_name, pay)
            print(f"Successfully proccessed payroll for {employee_name}!")
        except:
            print(f"Unexpected error occurred while calculating payroll deductions, skipping calculation for {employee_name}")
            print("Error:", sys.exc_info()[0])

if __name__ == "__main__":
    main()
