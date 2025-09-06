import csv
from models.account import Account
from datetime import datetime

ACCOUNT_FILE = "../data/accounts.csv"
TRANSACTIONS_FILE = "../data/transactions.log"
DETAILED_TRANSACTIONS_FILE = "../data/detailed_transactions.log"

def save_accounts(accounts):
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


def log_transaction(account_number, operation, amount, balance_after, details=None):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    details_str = f" | {details}" if details else ""

    # Log to main transaction file
    with open(TRANSACTIONS_FILE, "a") as f:
        f.write(f"{timestamp} | {account_number} | {operation} | {amount} | {balance_after}{details_str}\n")

    # Log detailed information for deposits and withdrawals to separate file
    if operation in ["DEPOSIT", "WITHDRAW", "TRANSFER_IN", "TRANSFER_OUT"]:
        with open(DETAILED_TRANSACTIONS_FILE, "a") as f:
            f.write(f"=== {operation} TRANSACTION ===\n")
            f.write(f"Timestamp: {timestamp}\n")
            f.write(f"Account Number: {account_number}\n")
            f.write(f"Operation: {operation}\n")
            f.write(f"Amount: {amount}\n")
            f.write(f"Balance After: {balance_after}\n")
            if details:
                f.write(f"Details: {details}\n")
            f.write(f"{'='*40}\n\n")

def get_transaction_history(account_number):
    """Get transaction history for a specific account"""
    transactions = []
    try:
        with open(TRANSACTIONS_FILE, "r") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue

                parts = line.split(" | ")
                if len(parts) >= 5:
                    timestamp, acc_num, operation, amount, balance = parts[:5]
                    details = " | ".join(parts[5:]) if len(parts) > 5 else ""

                    if int(acc_num) == int(account_number):
                        transactions.append({
                            "timestamp": timestamp,
                            "operation": operation,
                            "amount": amount,
                            "balance_after": balance,
                            "details": details
                        })
    except FileNotFoundError:
        pass
    except Exception as e:
        print(f"Error reading transaction history: {e}")

    return transactions

def export_accounts_to_file(accounts, filename):
    """Export all accounts to a CSV file"""
    try:
        with open(filename, "w", newline="") as f:
            writer = csv.writer(f)
            # Write header
            writer.writerow(["Account Number", "Name", "Age", "Account Type", "Balance", "Status", "PIN Set"])

            # Write account data
            for acc in accounts.values():
                writer.writerow([
                    acc.account_number,
                    acc.name,
                    acc.age,
                    acc.account_type,
                    f"{acc.balance:.2f}",
                    acc.status,
                    "Yes" if acc.pin else "No"
                ])
        return True, f"Accounts exported successfully to {filename}"
    except Exception as e:
        return False, f"Error exporting accounts: {e}"

def import_accounts_from_file(filename):
    """Import accounts from a CSV file"""
    imported_accounts = {}
    try:
        with open(filename, "r") as f:
            reader = csv.DictReader(f)
            for row in reader:
                # Skip if required fields are missing
                required_fields = ["Account Number", "Name", "Age", "Account Type", "Balance", "Status"]
                if not all(field in row and row[field].strip() for field in required_fields):
                    continue

                # Create account object
                acc = Account(
                    account_number=int(row["Account Number"]),
                    name=row["Name"],
                    age=int(row["Age"]),
                    account_type=row["Account Type"],
                    balance=float(row["Balance"]),
                    status=row["Status"],
                    pin=None  # PIN will need to be set separately for security
                )
                imported_accounts[acc.account_number] = acc

        return imported_accounts, f"Successfully imported {len(imported_accounts)} account(s)"
    except FileNotFoundError:
        return {}, f"File {filename} not found"
    except Exception as e:
        return {}, f"Error importing accounts: {e}"