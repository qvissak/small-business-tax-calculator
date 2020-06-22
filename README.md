# Oklahoma Payroll Calculator

Python script to calculate and save the payroll deductions for employees of a small business in Oklahoma.

## Set Up

Install Python3.

```bash
python3 -m venv env
source ./env/bin/activate
python3 -m pip install requests
```

## Run

Run the script without command line arguments. The program will prompt you for input.

```bash
python3 oklahoma-payroll.py
```

```bash
Payroll date (MM/DD/YYYY): 06/22/2020
Intuit filename: sample_input.csv
Successfully proccessed payroll for Peter Stone!
Successfully proccessed payroll for Mike Brown!
...
```

Alternatively, run the script with command line arguments.

```bash
python3 oklahoma-payroll.py 06/22/2020 sample_input.csv
```

```bash
Successfully proccessed payroll for Peter Stone!
Successfully proccessed payroll for Mike Brown!
...
```

### Add an Employee

When onboarding a new employee, after they fill out their 2020 W-4, add their information to [this CSV](./employees.csv).

> __NOTE__: The program only supports the format "FirstName LastName" for the `name` field. This will not work for individuals with two first names or two last names (non-hyphenated).

## Bundle

To create an executable, run:

```bash
pip3 install pyinstaller
pyinstaller --onefile oklahoma-payroll.py
```

To run:

```bash
./dist/oklahoma-payroll
```

Or:

```bash
./dist/oklahoma-payroll 06/22/2020 sample_input.csv
```
