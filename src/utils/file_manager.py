import csv
from models.account import Account
from datetime import datetime
import os

# Always resolve path relative to project root
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ACCOUNT_FILE = os.path.join(BASE_DIR, "data", "accounts.csv")
TRANSACTIONS_FILE = os.path.join(BASE_DIR, "data", "transactions.log")

def save_accounts(accounts):
    os.makedirs(os.path.dirname(ACCOUNT_FILE), exist_ok=True)
    with open(ACCOUNT_FILE, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["account_number", "name", "age", "balance", "account_type", "status", "pin"])
        for acc in accounts.values():
            d = acc.to_dict()
            writer.writerow(
                [
                    d["account_number"],
                    d["name"],
                    d["age"],
                    d["balance"],
                    d["account_type"],
                    d["status"],
                    d["pin"]
                    ])


def load_accounts():
    accounts = {}
    try:
        with open(ACCOUNT_FILE, "r") as f:
            reader = csv.DictReader(f)
            for row in reader:
                acc = Account(
                    account_number= row["account_number"],
                    name= row["name"],
                    age=row["age"],
                    account_type=row["account_type"],
                    balance=row["balance"],
                    status=row["status"],
                    pin=row["pin"] if row["pin"] else None
                )
                accounts[acc.account_number] = acc
    except FileNotFoundError:
        pass
    return accounts


def log_transaction(account_number, operation, amount, balance_after):
    os.makedirs(os.path.dirname(TRANSACTIONS_FILE), exist_ok=True)
    with open(TRANSACTIONS_FILE, "a") as f:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        f.write(f"{timestamp} | {account_number} | {operation} | {amount} | {balance_after}\n")