# This is the "service layer"
# It acts as the middle layer between  the Account model (business rules)
# and file_manager utilities (storage and logging).
from models.account import Account
from  utils.file_manager import load_accounts, save_accounts, log_transaction, get_transaction_history, export_accounts_to_file, import_accounts_from_file
from datetime import datetime, date
from collections import defaultdict
class BankingService:
    START_ACCOUNT_NO = 1001
    GLOBAL_MIN_BALANCE = 500  # Global minimum balance for withdrawals
    INTEREST_RATE = 0.05  # 5% annual interest rate
    DAILY_TRANSACTION_LIMIT = 50000  # Daily transaction limit
    def __init__(self):
        # load accounts from file on starup
        self.accounts = load_accounts()
        if self.accounts:
            # if account exist, continue from the max account number
            self.next_account_number = max(self.accounts.keys()) + 1 # 1001, 1002, 1003 , 1004
        else :
            # otherwise,start fresh from 1001
            self.next_account_number = BankingService.START_ACCOUNT_NO

        # Track daily transactions per account
        self.daily_transactions = defaultdict(lambda: defaultdict(float))  # {account_number: {date: total_amount}}
 
   
    def save_to_disk(self):
        #save all accounts to persistent storage(CSV files)
        save_accounts(self.accounts)
 
 
    def create_account(self, name,age, account_type, intial_deposit=0):
        # ---- Basic Validation Checks ----
        if not name.strip():
            return None, "Name cannot be empty"

        # Enhanced age verification with proper error handling
        try:
            age_int = int(age)
            if age_int < 0:
                return None, "Age cannot be negative"
            if age_int < 18:
                return None, "Account creation denied: Minimum age requirement is 18 years. Please contact a guardian for assistance."
            if age_int > 150:
                return None, "Invalid age: Please enter a valid age"
        except (ValueError, TypeError):
            return None, "Invalid age format: Please enter a valid number"
       
 
        # Normalize account type (capitalize first letter)
        account_type = account_type.title()
        if account_type not in Account.MIN_BALANCE:
            # check if account type is valid
            return None , f"Invalid Account type. Choose from {list(Account.MIN_BALANCE.keys())}"
        min_req = Account.MIN_BALANCE[account_type]
        if float(intial_deposit) < min_req:
            return None, f"Intial deposit must be at least {min_req}"
       
        acc_no = self.next_account_number
        acc = Account(acc_no, name, age_int, account_type, balance=float(intial_deposit))
        self.accounts[acc_no] = acc
        # 1001, 10002, 1003
        self.next_account_number += 1
 
 
        log_transaction(acc_no, "CREATE", intial_deposit, acc.balance)
        self.save_to_disk()
        return acc, "Account created succesfully"
   
 
    def get_account(self, account_number):
        return self.accounts.get(int(account_number))
   
 
    def deposit(self,account_number, amount):
        acc = self.get_account(account_number)
        if not acc:
            return False, "Account not Found"
        if acc.status != "Active":
            return False , "Account is not Active"

        # Check daily transaction limit
        try:
            amount_float = float(amount)
        except (TypeError, ValueError):
            return False, "Invalid amount"

        limit_ok, limit_msg = self._check_daily_limit(account_number, amount_float)
        if not limit_ok:
            return False, limit_msg

        ok, msg = acc.deposit(amount)
        if ok:
            self._update_daily_transactions(account_number, amount_float)
            log_transaction(acc.account_number, "DEPOSIT", amount, acc.balance)
            self.save_to_disk()
        return ok, msg
   
    def withdraw(self, account_number, amount):
        acc = self.get_account(account_number)
        if not acc:
            return False, "Account not Found"
        if acc.status != "Active":
            return False , "Account is not Active"

        # Additional global minimum balance check
        try:
            amount_float = float(amount)
        except (TypeError, ValueError):
            return False, "Invalid amount"

        if acc.balance - amount_float < BankingService.GLOBAL_MIN_BALANCE:
            return False, f"Withdrawal denied. Balance cannot go below global minimum of {BankingService.GLOBAL_MIN_BALANCE}"

        # Check daily transaction limit
        limit_ok, limit_msg = self._check_daily_limit(account_number, amount_float)
        if not limit_ok:
            return False, limit_msg

        ok, msg = acc.withdraw(amount)
        if ok:
            self._update_daily_transactions(account_number, amount_float)
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
    
    #searching by name
    def search_by_name(self, name):
        if not name.strip():
            return [],"Name cannot be empty"
       
        results = []
        for acc in self.accounts.values():
            if name.lower() in acc.name.lower():
                results.append(acc)

        if not results:
            return [], "No accounts found for the given name"
        return results, f"Found {len(results)} accounts for the given name"
    
    #search by account number
    def search_by_account_number(self, account_number):
        """Search for an account by account number"""
        try:
            acc_num = int(account_number)
            acc = self.get_account(acc_num)
            if not acc:
                return None, f"No account found with number {acc_num}"
            return acc, "Account found"
        except ValueError:
            return None, "Invalid account number format"
    
    def list_active_accounts(self):
        """List all active accounts"""
        active_accounts = [acc for acc in self.accounts.values() if acc.status == "Active"]
        if not active_accounts:
            return [], "No active accounts found"
        return active_accounts, f"Found {len(active_accounts)} active account(s)"
    
    def list_closed_accounts(self):
        """List all closed/inactive accounts"""
        closed_accounts = [acc for acc in self.accounts.values() if acc.status == "Inactive"]
        if not closed_accounts:
            return [], "No closed accounts found"
        return closed_accounts, f"Found {len(closed_accounts)} closed account(s)"
    
    def reopen_account(self, account_number):
        """Reopen a closed account"""
        acc = self.get_account(account_number)
        if not acc:
            return False, "Account not found"
        
        if acc.status == "Active":
            return False, "Account is already active"
        
        acc.status = "Active"
        log_transaction(acc.account_number, "REOPEN", None, acc.balance)
        self.save_to_disk()
        return True, "Account reopened successfully"
    
    def rename_account_holder(self, account_number, new_name):
        """Rename the account holder"""
        if not new_name.strip():
            return False, "New name cannot be empty"
        
        acc = self.get_account(account_number)
        if not acc:
            return False, "Account not found"
        
        old_name = acc.name
        acc.name = new_name.strip()
        log_transaction(acc.account_number, "RENAME", None, acc.balance, 
                       details=f"Name changed from '{old_name}' to '{new_name}'")
        self.save_to_disk()
        return True, f"Account holder name changed to {new_name}"
    
    def delete_all_accounts(self):
        """Delete all accounts"""
        if not self.accounts:
            return False, "No accounts to delete"
        
        count = len(self.accounts)
        self.accounts.clear()
        self.next_account_number = BankingService.START_ACCOUNT_NO
        self.save_to_disk()
        return True, f"All {count} account(s) have been deleted"
    
    def count_active_accounts(self):
        """Count the number of active accounts"""
        active_count = sum(1 for acc in self.accounts.values() if acc.status == "Active")
        return active_count, f"Total active accounts: {active_count}"

    def upgrade_account_type(self, account_number, new_account_type):
        """Upgrade account type (e.g., Savings to Current)"""
        acc = self.get_account(account_number)
        if not acc:
            return False, "Account not found"

        if acc.status != "Active":
            return False, "Account must be active to upgrade"

        # Normalize account type
        new_account_type = new_account_type.title()
        if new_account_type not in Account.MIN_BALANCE:
            return False, f"Invalid account type. Choose from {list(Account.MIN_BALANCE.keys())}"

        if acc.account_type == new_account_type:
            return False, f"Account is already of type {new_account_type}"

        # Check if current balance meets minimum requirement for new account type
        min_required = Account.MIN_BALANCE[new_account_type]
        if acc.balance < min_required:
            return False, f"Insufficient balance for {new_account_type} account. Minimum required: {min_required}"

        old_type = acc.account_type
        acc.account_type = new_account_type
        log_transaction(acc.account_number, "UPGRADE", None, acc.balance,
                       details=f"Account type changed from {old_type} to {new_account_type}")
        self.save_to_disk()
        return True, f"Account type upgraded from {old_type} to {new_account_type}"

    def calculate_simple_interest(self, account_number, time_years=1):
        """Calculate simple interest on account balance"""
        acc = self.get_account(account_number)
        if not acc:
            return None, "Account not found"

        if acc.status != "Active":
            return None, "Account must be active to calculate interest"

        try:
            time_years = float(time_years)
            if time_years <= 0:
                return None, "Time period must be positive"
        except (TypeError, ValueError):
            return None, "Invalid time period"

        principal = acc.balance
        interest = principal * BankingService.INTEREST_RATE * time_years
        total_amount = principal + interest

        return {
            "principal": principal,
            "interest_rate": BankingService.INTEREST_RATE,
            "time_years": time_years,
            "interest_earned": interest,
            "total_amount": total_amount
        }, f"Interest calculation completed for account {account_number}"

    def _check_daily_limit(self, account_number, amount):
        """Check if transaction exceeds daily limit"""
        today = date.today().isoformat()
        current_daily_total = self.daily_transactions[account_number][today]

        if current_daily_total + amount > BankingService.DAILY_TRANSACTION_LIMIT:
            return False, f"Daily transaction limit exceeded. Limit: {BankingService.DAILY_TRANSACTION_LIMIT}, Current total: {current_daily_total}"

        return True, "Within daily limit"

    def _update_daily_transactions(self, account_number, amount):
        """Update daily transaction tracking"""
        today = date.today().isoformat()
        self.daily_transactions[account_number][today] += amount

    def transfer_funds(self, from_account, to_account, amount):
        """Transfer funds from one account to another"""
        # Validate accounts
        from_acc = self.get_account(from_account)
        to_acc = self.get_account(to_account)

        if not from_acc:
            return False, f"Source account {from_account} not found"
        if not to_acc:
            return False, f"Destination account {to_account} not found"

        if from_acc.status != "Active":
            return False, "Source account is not active"
        if to_acc.status != "Active":
            return False, "Destination account is not active"

        if from_account == to_account:
            return False, "Cannot transfer to the same account"

        # Validate amount
        try:
            amount_float = float(amount)
        except (TypeError, ValueError):
            return False, "Invalid amount"

        if amount_float <= 0:
            return False, "Transfer amount must be positive"

        # Check daily limits for both accounts
        from_limit_ok, from_limit_msg = self._check_daily_limit(from_account, amount_float)
        if not from_limit_ok:
            return False, f"Source account: {from_limit_msg}"

        to_limit_ok, to_limit_msg = self._check_daily_limit(to_account, amount_float)
        if not to_limit_ok:
            return False, f"Destination account: {to_limit_msg}"

        # Check if source account has sufficient funds
        min_required = max(Account.MIN_BALANCE[from_acc.account_type], BankingService.GLOBAL_MIN_BALANCE)
        if from_acc.balance - amount_float < min_required:
            return False, f"Insufficient funds. Minimum required balance: {min_required}"

        # Perform the transfer
        from_acc.balance -= amount_float
        to_acc.balance += amount_float

        # Update daily transaction tracking
        self._update_daily_transactions(from_account, amount_float)
        self._update_daily_transactions(to_account, amount_float)

        # Log transactions
        log_transaction(from_account, "TRANSFER_OUT", amount_float, from_acc.balance,
                       details=f"Transfer to account {to_account}")
        log_transaction(to_account, "TRANSFER_IN", amount_float, to_acc.balance,
                       details=f"Transfer from account {from_account}")

        self.save_to_disk()
        return True, f"Successfully transferred {amount_float} from account {from_account} to account {to_account}"

    def get_transaction_history(self, account_number):
        """Get transaction history for a specific account"""
        acc = self.get_account(account_number)
        if not acc:
            return [], "Account not found"

        transactions = get_transaction_history(account_number)
        if not transactions:
            return [], f"No transaction history found for account {account_number}"

        return transactions, f"Found {len(transactions)} transaction(s) for account {account_number}"

    def calculate_average_balance(self):
        """Calculate average balance across all accounts"""
        if not self.accounts:
            return 0, "No accounts found"

        total_balance = sum(acc.balance for acc in self.accounts.values())
        average_balance = total_balance / len(self.accounts)

        return average_balance, f"Average balance across {len(self.accounts)} account(s): {average_balance:.2f}"

    def get_youngest_account_holder(self):
        """Get the youngest account holder"""
        if not self.accounts:
            return None, "No accounts found"

        youngest_acc = min(self.accounts.values(), key=lambda acc: acc.age)
        return youngest_acc, f"Youngest account holder: {youngest_acc.name} (Age: {youngest_acc.age})"

    def get_oldest_account_holder(self):
        """Get the oldest account holder"""
        if not self.accounts:
            return None, "No accounts found"

        oldest_acc = max(self.accounts.values(), key=lambda acc: acc.age)
        return oldest_acc, f"Oldest account holder: {oldest_acc.name} (Age: {oldest_acc.age})"

    def get_top_accounts_by_balance(self, n=5):
        """Get top N accounts sorted by balance"""
        if not self.accounts:
            return [], "No accounts found"

        try:
            n = int(n)
            if n <= 0:
                return [], "Number of accounts must be positive"
        except (TypeError, ValueError):
            return [], "Invalid number format"

        # Sort accounts by balance in descending order
        sorted_accounts = sorted(self.accounts.values(), key=lambda acc: acc.balance, reverse=True)
        top_accounts = sorted_accounts[:n]

        return top_accounts, f"Top {len(top_accounts)} account(s) by balance"

    def set_pin(self, account_number, pin):
        """Set PIN for an account"""
        acc = self.get_account(account_number)
        if not acc:
            return False, "Account not found"

        # Validate PIN format (4-digit numeric)
        if not pin.isdigit() or len(pin) != 4:
            return False, "PIN must be exactly 4 digits"

        acc.pin = pin
        log_transaction(acc.account_number, "SET_PIN", None, acc.balance, details="PIN set")
        self.save_to_disk()
        return True, "PIN set successfully"

    def verify_pin(self, account_number, pin):
        """Verify PIN for an account"""
        acc = self.get_account(account_number)
        if not acc:
            return False, "Account not found"

        if not acc.pin:
            return False, "No PIN set for this account"

        if acc.pin != pin:
            return False, "Incorrect PIN"

        return True, "PIN verified"

    def change_pin(self, account_number, old_pin, new_pin):
        """Change PIN for an account"""
        acc = self.get_account(account_number)
        if not acc:
            return False, "Account not found"

        # Verify old PIN
        verify_ok, verify_msg = self.verify_pin(account_number, old_pin)
        if not verify_ok:
            return False, f"PIN verification failed: {verify_msg}"

        # Set new PIN
        return self.set_pin(account_number, new_pin)

    def export_accounts(self, filename=None):
        """Export all accounts to a CSV file"""
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"../data/accounts_export_{timestamp}.csv"

        return export_accounts_to_file(self.accounts, filename)

    def import_accounts(self, filename):
        """Import accounts from a CSV file"""
        imported_accounts, msg = import_accounts_from_file(filename)

        if not imported_accounts:
            return False, msg

        # Check for account number conflicts
        conflicts = []
        for acc_num in imported_accounts.keys():
            if acc_num in self.accounts:
                conflicts.append(acc_num)

        if conflicts:
            return False, f"Account number conflicts found: {conflicts}. Import cancelled."

        # Add imported accounts
        self.accounts.update(imported_accounts)

        # Update next account number
        if self.accounts:
            self.next_account_number = max(self.accounts.keys()) + 1

        # Log import operation
        for acc in imported_accounts.values():
            log_transaction(acc.account_number, "IMPORT", None, acc.balance,
                           details=f"Account imported from {filename}")

        self.save_to_disk()
        return True, f"Successfully imported {len(imported_accounts)} account(s) from {filename}"

    def safe_exit(self):
        """Safely exit the application with autosave"""
        try:
            self.save_to_disk()
            return True, "All data saved successfully. Safe to exit."
        except Exception as e:
            return False, f"Error saving data: {e}. Please try again."