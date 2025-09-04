# This is the "service layer"
from models.account import Account
from utils.file_manager import save_accounts, load_accounts, log_transaction

class BankingService:
    START_ACCOUNT_NO = 1001

    def __init__(self):
        # Load accounts from file on startup
        self.accounts = load_accounts()
        if self.accounts:
            self.next_account_number = max(self.accounts.keys()) + 1
        else:
            self.next_account_number = BankingService.START_ACCOUNT_NO

    def save_to_disk(self):
        save_accounts(self.accounts)

    def create_account(self, name, age, account_type, initial_deposit=0):
        # Basic validation
        if not name.strip():
            return None, "Name cannot be empty"
        if int(age) < 18:
            return None, "Age must be 18 or above"

        account_type = account_type.title()
        if account_type not in Account.MIN_BALANCE:
            return None, f"Invalid account type. Choose from {list(Account.MIN_BALANCE.keys())}"

        min_req = Account.MIN_BALANCE[account_type]
        if float(initial_deposit) < min_req:
            return None, f"Initial deposit must be at least {min_req}"

        acc_no = self.next_account_number
        acc = Account(acc_no, name, age, account_type, balance=float(initial_deposit))
        self.accounts[acc_no] = acc
        self.next_account_number += 1

        log_transaction(acc_no, "CREATE", initial_deposit, acc.balance)
        self.save_to_disk()
        return acc, "Account created successfully"

    def get_account(self, account_number):
        return self.accounts.get(int(account_number))

    def deposit(self, account_number, amount):
        acc = self.get_account(account_number)
        if not acc:
            return False, "Account not found"
        if acc.status != "Active":
            return False, "Account is not active"
        ok, msg = acc.deposit(amount)
        if ok:
            log_transaction(acc.account_number, "DEPOSIT", amount, acc.balance)
            self.save_to_disk()
        return ok, msg

    def withdraw(self, account_number, amount):
        acc = self.get_account(account_number)
        if not acc:
            return False, "Account not found"
        if acc.status != "Active":
            return False, "Account is not active"
        ok, msg = acc.withdraw(amount)
        if ok:
            log_transaction(acc.account_number, "WITHDRAW", amount, acc.balance)
            self.save_to_disk()
        return ok, msg

    def balance_inquiry(self, account_number):
        acc = self.get_account(account_number)
        if not acc:
            return None, "Account not found"
        return acc, f"Balance: {acc.balance:.2f}"

    def close_account(self, account_number):
        acc = self.get_account(account_number)
        if not acc:
            return False, "Account not found"
        acc.status = "Inactive"
        log_transaction(acc.account_number, "CLOSE", None, acc.balance)
        self.save_to_disk()
        return True, "Account closed successfully"
 