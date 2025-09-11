import os, sys, csv
# Minimal import fix: add the project src/ folder to sys.path so
# "from models..." works when running this file directly.
sys.path.append(os.path.dirname(os.path.dirname(__file__)))
from models.account import Account
from datetime import datetime

ACCOUNT_FILE = "../data/accounts.csv"
TRANSACTIONS_FILE = "../data/transactions.log"

def save_accounts(accounts):
    with open(ACCOUNT_FILE, "w", newline="") as f:
        '''this opens the file in write mode and 
        newline="" prevents extra blank lines in csv on Windows 
        in simple words it makes sure that there are no extra blank lines in the csv file when we write to it
        and if the file does not exist it will create a new file
        if the file exists it will overwrite the existing file
        it stores the file object(means the file that we opened) in the variable f
        '''
        writer = csv.writer(f)
        '''this creates a csv writer object which is an inbuilt function in python that allows us to write to a csv file'''
        writer.writerow(["account_number", "name", "age", "balance", "account_type", "status", "pin", "failed_attempts"])
        '''this writes the header row to the csv file
        for example if the csv file has columns name,age,balance
        then the header row will be like name,age,balance'''
        for acc in accounts.values():
            '''this iterates through each account in the accounts dictionary'''
            d = acc.to_dict()
            '''this converts the account object to a dictionary'''
            writer.writerow(
                [
                    d["account_number"],
                    d["name"],
                    d["age"],
                    d["balance"],
                    d["account_type"],
                    d["status"],
                    d["pin"],
                    d["failed_attempts"]
                    ])#this writes the account details to the csv file


def load_accounts():
    accounts = {}#this creates an empty dictionary to store accounts
    try:
        with open(ACCOUNT_FILE, "r") as f:#this opens the file in read mode
            reader = csv.DictReader(f)
            '''this reads the file as a dictionary
            for example if the csv file has columns name,age,balance
            then the dictionary will be like {"name": "value", "age": "value", "balance": "value"}'''
            for row in reader:
                '''this iterates through each row of the csv file
                 and row is a dictionary representing each row
                 for example if the csv file has columns name,age,balance
                 then row will be like {"name": "value", "age": "value", "balance": "value"}
                 so we can access the values using row["name"], row["age"], row["balance"]'''
                # Skip empty rows
                if not row["account_number"]:
                    continue
                    
                acc = Account(
                    account_number=row["account_number"],
                    name=row["name"],
                    age=row["age"],
                    account_type=row["account_type"],
                    balance=float(row["balance"]),
                    status=row["status"],
                    pin=int(row["pin"]) if row["pin"] and row["pin"].strip() else None,
                    failed_attempts=int(row.get("failed_attempts", 0)),
                )
                accounts[acc.account_number] = acc #this adds the account object which contains all the details of the account to the accounts dictionary with account number as key
    except FileNotFoundError:
        pass
    return accounts


def log_transaction(account_number, operation, amount, balance_after):
    with open(TRANSACTIONS_FILE, "a") as f:#this opens the file in append mode(it will add new data  to the end of the file) and if the file does not exist it will create a new file and store the file object in the variable f
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")#this gets the current date and time and formats it as a string in the format YYYY-MM-DD HH:MM:SS
        f.write(f"{timestamp} | {account_number} | {operation} | {amount} | {balance_after}\n")#this writes the transaction details to the file in the format timestamp | account_number | operation | amount | 
        
def load_transactions():
    transactions = []
    try:
        with open(TRANSACTIONS_FILE, "r") as f:
            reader = csv.reader(f, delimiter='|')
            for row in reader:
                # Remove leading/trailing spaces from each element
                cleaned = [col.strip() for col in row]
                # Skip empty rows
                if cleaned and len(cleaned) >= 5:
                    transactions.append(cleaned)
    except FileNotFoundError:
        pass
    return transactions