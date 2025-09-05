# This is the "service layer"
# It acts as the middle layer between  the Account model (business rules)
# and file_manager utilities (storage and logging).
from models.account import Account
from  utils.file_manager import load_accounts, save_accounts, log_transaction
class BankingService:
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
        min_req = Account.MIN_BALANCE(account_type)
        if float(intial_deposit) < min_req:
            return None, f"Intial deposit must be at least {min_req}"
       
        acc_no = self.next_account_number
        acc = Account(acc_no, name,age, account_type, balance=float(intial_deposit))
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
        if acc.staus != "Active":
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
        if acc.staus != "Active":
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
        return results
    
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
        acc = self.get_account(account_number)
        if not acc:
            return None, "Account not Found"
        return acc, "Account found"