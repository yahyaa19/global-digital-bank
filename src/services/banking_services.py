# This is the "service layer"
# It acts as the middle layer between  the Account model (business rules)
# and file_manager utilities (storage and logging).
from models.account import Account
from utils.file_manager import load_accounts, save_accounts, log_transaction

class BankingService:
    def export_accounts(self, file_path):
        import csv
        with open(file_path, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["account_number", "name", "age", "balance", "account_type", "status", "pin"])
            for acc in self.accounts.values():
                d = acc.to_dict()
                writer.writerow([
                    d["account_number"], d["name"], d["age"], d["balance"], d["account_type"], d["status"], d["pin"]
                ])
        return True, f"Accounts exported to {file_path}"

    def import_accounts(self, file_path):
        import csv
        from models.account import Account
        count = 0
        with open(file_path, "r") as f:
            reader = csv.DictReader(f)
            for row in reader:
                acc = Account(
                    account_number=row["account_number"],
                    name=row["name"],
                    age=row["age"],
                    account_type=row["account_type"],
                    balance=row["balance"],
                    status=row["status"],
                    pin=row["pin"] if "pin" in row else None
                )
                self.accounts[int(row["account_number"])] = acc
                count += 1
        self.save_to_disk()
        return True, f"Imported {count} accounts from {file_path}"

    def verify_pin(self, account_number, pin):
        acc = self.get_account(account_number)
        if not acc:
            return False, "Account not found"
        if str(acc.pin) == str(pin):
            return True, "PIN verified"
        return False, "Incorrect PIN"

    def autosave(self):
        self.save_to_disk()
        return True, "All changes saved."
    def top_n_accounts_by_balance(self, n=5, active_only=True):
        accounts = self.list_active_accounts() if active_only else list(self.accounts.values())
        return sorted(accounts, key=lambda acc: acc.balance, reverse=True)[:n]

    def average_balance(self, active_only=True):
        accounts = self.list_active_accounts() if active_only else list(self.accounts.values())
        if not accounts:
            return 0.0
        return sum(acc.balance for acc in accounts) / len(accounts)

    def youngest_account_holder(self):
        accounts = self.list_active_accounts()
        if not accounts:
            return None
        return min(accounts, key=lambda acc: acc.age)

    def oldest_account_holder(self):
        accounts = self.list_active_accounts()
        if not accounts:
            return None
        return max(accounts, key=lambda acc: acc.age)

    def simple_interest(self, account_number, rate, years):
        acc = self.get_account(account_number)
        if not acc:
            return None, "Account not found"
        try:
            principal = float(acc.balance)
            rate = float(rate)
            years = float(years)
        except:
            return None, "Invalid input"
        interest = principal * rate * years / 100
        return interest, f"Simple Interest for {years} years at {rate}%: {interest}"
    DAILY_LIMIT = 200000.0  # Example daily limit

    def get_transaction_history(self, account_number):
        from utils.file_manager import TRANSACTIONS_FILE
        history = []
        try:
            with open(TRANSACTIONS_FILE, "r") as f:
                for line in f:
                    if f"| {account_number} |" in line:
                        history.append(line.strip())
        except FileNotFoundError:
            pass
        return history

    def get_today_total(self, account_number):
        from utils.file_manager import TRANSACTIONS_FILE
        from datetime import datetime
        today = datetime.now().strftime("%Y-%m-%d")
        total = 0.0
        try:
            with open(TRANSACTIONS_FILE, "r") as f:
                for line in f:
                    if f"| {account_number} |" in line and line.startswith(today):
                        parts = line.split("|")
                        op = parts[2].strip()
                        amt = parts[3].strip()
                        if op in ["DEPOSIT", "WITHDRAW", "TRANSFER_OUT", "TRANSFER_IN"]:
                            try:
                                total += float(amt)
                            except:
                                pass
        except FileNotFoundError:
            pass
        return total

    def transfer_funds(self, from_acc_no, to_acc_no, amount):
        from_acc = self.get_account(from_acc_no)
        to_acc = self.get_account(to_acc_no)
        if not from_acc or not to_acc:
            return False, "One or both accounts not found."
        if from_acc.status != "Active" or to_acc.status != "Active":
            return False, "Both accounts must be active."
        try:
            amount = float(amount)
        except:
            return False, "Invalid amount."
        # Minimum balance check for sender
        min_required = Account.MIN_BALANCE[from_acc.account_type]
        if from_acc.balance - amount < min_required:
            return False, f"Insufficient funds. Minimum required balance for {from_acc.account_type}: {min_required}"
        # Daily limit check for sender
        today_total = self.get_today_total(from_acc_no)
        if today_total + amount > self.DAILY_LIMIT:
            return False, f"Daily transaction limit ({self.DAILY_LIMIT}) exceeded."
        # Transfer
        from_acc.balance -= amount
        to_acc.balance += amount
        log_transaction(from_acc_no, "TRANSFER_OUT", amount, from_acc.balance)
        log_transaction(to_acc_no, "TRANSFER_IN", amount, to_acc.balance)
        self.save_to_disk()
        return True, f"Transferred {amount} from {from_acc_no} to {to_acc_no}."
    def search_by_name(self, name):
        name = name.strip().lower()
        return [acc for acc in self.accounts.values() if acc.name.lower() == name]

    def search_by_account_number(self, account_number):
        return self.accounts.get(int(account_number))

    def list_active_accounts(self):
        return [acc for acc in self.accounts.values() if acc.status == "Active"]

    def list_closed_accounts(self):
        return [acc for acc in self.accounts.values() if acc.status == "Inactive"]

    def reopen_closed_account(self, account_number):
        acc = self.get_account(account_number)
        if not acc:
            return False, "Account not Found"
        if acc.status == "Active":
            return False, "Account is already active"
        acc.status = "Active"
        log_transaction(acc.account_number, "REOPEN", None, acc.balance)
        self.save_to_disk()
        return True, "Account reopened successfully"

    def rename_account_holder(self, account_number, new_name):
        acc = self.get_account(account_number)
        if not acc:
            return False, "Account not Found"
        if acc.status != "Active":
            return False, "Account is not Active"
        acc.name = new_name.strip()
        log_transaction(acc.account_number, "RENAME", None, acc.balance)
        self.save_to_disk()
        return True, "Account holder renamed successfully"

    def delete_all_accounts(self):
        self.accounts.clear()
        self.save_to_disk()
        return True, "All accounts deleted"

    def count_active_accounts(self):
        return len([acc for acc in self.accounts.values() if acc.status == "Active"])
    START_ACCOUNT_NO = 1001

    def __init__(self):
        # load accounts from file on starup
        self.accounts = load_accounts()
        if self.accounts:
            # if account exist, continue from the max account number
            self.next_account_number = max(self.accounts.keys()) + 1 # 1001, 1002, 1003 , 1004
        else :
            # otherwise,start fresh from 1001
            self.next_account_number = BankingService.START_ACCOUNT_NO
 
   
    def save_to_disk(self):
        #save all accounts to persistent storage(CSV files)
        save_accounts(self.accounts)
 
 
    def create_account(self, name,age, account_type, intial_deposit=0):
        # ---- Basic Validation Checks ----
        if not name.strip():
            return None, "Name cannot be empty"
       
        if int(age) < 18:
            return None, "Age must be 18 or above"
       
 
        # Normalize account type (capitalize first letter)
        account_type = account_type.title()
        if account_type not in Account.MIN_BALANCE:
            # check if account type is valid
            return None , f"Invalid Account type. Choose from {list(Account.MIN_BALANCE.keys())}"
        min_req = Account.MIN_BALANCE[account_type]

        if float(intial_deposit) < min_req:
            return None, f"Intial deposit must be at least {min_req}"
       
        acc_no = self.next_account_number
        acc = Account(acc_no, name, age, account_type, balance=float(intial_deposit))
        self.accounts[acc_no] = acc
        # 1001, 10002, 1003
        self.next_account_number += 1

        log_transaction(acc_no, "CREATE", intial_deposit, acc.balance)
        self.save_to_disk()  # Persist accounts to CSV after creation
        return acc, "Account created succesfully"
   
 
    def get_account(self, account_number):
        return self.accounts.get(int(account_number))
   
 
    def deposit(self,account_number, amount):
        acc = self.get_account(account_number)
        if not acc:
            return False, "Account not Found"
        if acc.status != "Active":
            return False , "Account is not Active"
       
        ok, msg = acc.deposit(amount)
        if ok:
            log_transaction(acc.account_number, "DEPOSIT", amount, acc.balance)
            self.save_to_disk()
        return ok, msg
   
    def withdraw(self, account_number, amount):
        acc = self.get_account(account_number)
        if not acc:
            return False, "Account not Found"
        if acc.status != "Active":
            return False , "Account is not Active"
       
        ok, msg = acc.withdraw(amount)
        if ok:
            log_transaction(acc.account_number, "WITHDRAW", amount, acc.balance)
            self.save_to_disk()
        return ok, msg
   
    def balance_inquiry(self, account_number):
        acc = self.get_account(account_number)
        if not acc:
            return False, "Account not Found"
        return acc, f"Balance: {acc.balance: .2f}"
   
    def close_account(self, account_number):
         acc = self.get_account(account_number)
         if not acc:
            return False, "Account not Found"
         
         acc.status = "Inactive"
         log_transaction(acc.account_number, "CLOSE" , None, acc.balance)
         self.save_to_disk()
         return True , "Account closed succesfully"