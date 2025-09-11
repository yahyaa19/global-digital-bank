# This is the "service layer"
# It acts as the middle layer between  the Account model (business rules)
# and file_manager utilities (storage and logging).
from models.account import Account
from utils.file_manager import load_accounts, save_accounts, log_transaction, load_transactions
class BankingService:
    """Coordinates account operations between the Account model and file I/O.

    This class is the high-level API the rest of the app should use. It:
    - Loads all accounts when created
    - Creates accounts after validating inputs
    - Finds an account by number
    - Performs deposits and withdrawals by delegating to Account methods
    - Persists changes and logs each operation
    """
    START_ACCOUNT_NO = 1001
    def __init__(self):
        """Initialize the service by loading accounts and setting the next number.

        Steps:
        1) Load previously saved accounts via load_accounts() (returns dict[int, Account]).
        2) If any exist, compute the next account number as max(existing)+1.
           Otherwise start from START_ACCOUNT_NO.
        """
        # load accounts from file on starup
        self.accounts = load_accounts()
        if self.accounts:
            # if account exist, continue from the max account number
            self.next_account_number = max(self.accounts.keys()) + 1 # 1001, 1002, 1003 , 1004
        else :
            # otherwise,start fresh from 1001
            self.next_account_number = BankingService.START_ACCOUNT_NO
 
   
    def save_to_disk(self):
        """Write all current accounts to disk using save_accounts().

        This persists the in-memory state so it can be reloaded later.
        """
        #save all accounts to persistent storage(CSV files)
        save_accounts(self.accounts)
 
 
    def create_account(self, name, age, account_type, initial_deposit=0, pin=None):
        """Create a new account after validating inputs.

        Parameters:
        - name: string with the account holder's name
        - age: integer-like value; must be >= 18
        - account_type: string; must be one of the keys in Account.MIN_BALANCE
        - initial_deposit: number-like; must be >= the type's minimum balance
        - pin: optional PIN for the account

        Flow:
        1) Validate name is not empty.
        2) Validate age is >= 18.
        3) Normalize account_type (e.g., "savings" -> "Savings") and verify it's allowed.
        4) Ensure the initial deposit meets the minimum balance for that type.
        5) Allocate a new account number, build an Account instance, store it in self.accounts.
        6) Increment the sequence, log the creation, save to disk, return (Account, message).

        Note on current implementation details:
        - Account.MIN_BALANCE is a dict, so getting the minimum should use
          Account.MIN_BALANCE[account_type]. The code below calls it like a function,
          which will raise a TypeError at runtime. This will be fixed in a later edit.
        - The parameter is spelled intial_deposit (missing 'i'). This is fine for now
          as long as callers use the same name; we'll correct naming in a later pass.
        """
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
        # Get the minimum required balance for this account type.
        min_req = Account.MIN_BALANCE[account_type]
        if float(initial_deposit) < min_req:
            return None, f"Intial deposit must be at least {min_req}"
       
        # Allocate a fresh account number from the sequence.
        acc_no = self.next_account_number
        # Build a new Account object and store it in the dictionary.
        acc = Account(acc_no, name, age, account_type, balance=float(initial_deposit), pin=pin)
        self.accounts[acc_no] = acc
        # 1001, 10002, 1003
        self.next_account_number += 1
 
 
        # Record this operation in the transaction log for auditing.
        log_transaction(acc_no, "CREATE", initial_deposit, acc.balance)
        # Persist the latest state so this account exists on disk.
        self.save_to_disk()
        return acc, "Account created succesfully"
   
 
    def get_account(self, account_number):
        """Return the Account object for a given number, or None if missing.

        Converts the provided account_number to int to match the dictionary keys.
        """
        return self.accounts.get(int(account_number))
   
    def get_account_by_name(self, name):
        
        for acc in self.accounts.values():
            if acc.name.lower() == name.lower():
                print("Account found:\n")
                return acc

        return None
 
    def deposit(self,account_number, amount, pin):
        """Deposit money into an account and persist/log if successful.

        Steps:
        1) Look up the account. If not found, return an error.
        2) Ensure the account is Active. If not, return an error.
        3) Validate PIN if set.
        4) Call the Account.deposit(amount) method, which validates amount and updates balance.
        5) If the deposit succeeds, log the operation and save all accounts to disk.
        6) Return the result from the Account method.
        """
        acc = self.get_account(account_number)
        if not acc:
            return False, "Account not Found"
        # Ensure the account is active
        if acc.status != "Active":
            return False , "Account is not Active"
        # Check if account is locked due to too many failed attempts
        if acc.is_locked():
            return False, "Account is locked due to too many failed PIN attempts. Please contact support."
        
        # Validate PIN if set - continuous checking until correct or locked
        if acc.pin is not None:
            while acc.failed_attempts <= acc.max_attempts:
                if pin == acc.pin:
                    # PIN is correct, reset failed attempts
                    acc.reset_failed_attempts()
                    self.save_to_disk()
                    break
                else:
                    # PIN is incorrect, increment failed attempts
                    acc.increment_failed_attempts()
                    self.save_to_disk()
                    remaining_attempts = acc.max_attempts - acc.failed_attempts
                    
                    if acc.is_locked():
                        return False, f"Account locked! Too many failed attempts. Please contact support."
                    else:
                        print(f"Invalid PIN. {remaining_attempts} attempts remaining.")
                        pin = int(input("Enter your pin again: "))
            
            # If we exit the loop and still locked, return error
            if acc.is_locked():
                return False, f"Account locked! Too many failed attempts. Please contact support."
        
        ok, msg = acc.deposit(amount)
        if ok:
            log_transaction(acc.account_number, "DEPOSIT", amount, acc.balance)
            self.save_to_disk()
        return ok, msg
    
    def withdraw(self, account_number, amount, pin):
        """Withdraw money from an account and persist/log if successful.

        Steps:
        1) Look up the account; error if missing.
        2) Ensure the account is Active.
        3) Validate PIN if set.
        4) Call Account.withdraw(amount); Account enforces min balance rules per type.
        5) If it succeeds, log and save to disk.
        6) Return the result tuple.
        """
        acc = self.get_account(account_number)# get_account is a method of
        if not acc:
            return False, "Account not Found"
        # Ensure the account is active
        if acc.status != "Active":
            return False, "Account is not Active"
        # Check if account is locked due to too many failed attempts
        if acc.is_locked():
            return False, "Account is locked due to too many failed PIN attempts. Please contact support."
        
        # Validate PIN if set - continuous prompting until correct or locked
        if acc.pin is not None:
            while acc.failed_attempts < acc.max_attempts:
                if pin == acc.pin:
                    # PIN is correct, reset failed attempts
                    acc.reset_failed_attempts()
                    self.save_to_disk()
                    break
                else:
                    # PIN is incorrect, increment failed attempts
                    acc.increment_failed_attempts()
                    self.save_to_disk()
                    remaining_attempts = acc.max_attempts - acc.failed_attempts
                    
                    if acc.is_locked():
                        return False, f"Account locked! Too many failed attempts. Please contact support."
                    else:
                        print(f"Invalid PIN. {remaining_attempts} attempts remaining.")
                        pin = int(input("Enter your pin again: "))
            
            # If we exit the loop and still locked, return error
            if acc.is_locked():
                return False, f"Account locked! Too many failed attempts. Please contact support."
        
        ok, msg = acc.withdraw(amount)
        if ok:
            log_transaction(acc.account_number, "WITHDRAW", amount, acc.balance)
            self.save_to_disk()
        return ok, msg

    def transfer(self,from_ac,to_acc,pin,amount):
        from_acc = self.get_account(from_ac)
        to_acc = self.get_account(to_acc)
        if not from_acc:
            return False,"Sender Account not Found"
        if not to_acc:
            return False,"Receiver Account not Found"
        if from_acc.status != "Active":
            return False,"Sender Account is not Active. Please contact support and activate the sender account first."
        if to_acc.status != "Active":
            return False,"Receiver Account is not Active. Please contact support and activate the receiver account first."
        if from_acc.is_locked():
            return False, "Sender Account is locked. Please contact support and unlock the sender account first."
        if to_acc.is_locked():
            return False, "Receiver Account is locked. Please contact support and unlock the receiver account first."
        if from_acc.pin is not None:
            while from_acc.failed_attempts < from_acc.max_attempts:
                if pin == from_acc.pin:
                    # PIN is correct, reset failed attempts
                    from_acc.reset_failed_attempts()
                    self.save_to_disk()
                    break
                else:
                    # PIN is incorrect, increment failed attempts
                    from_acc.increment_failed_attempts()
                    self.save_to_disk()
                    remaining_attempts = from_acc.max_attempts - from_acc.failed_attempts
                    print(f"Invalid PIN. {remaining_attempts} attempts remaining.")
                    pin = int(input("Enter your pin again: "))
        if from_acc.is_locked():
            return False, f"Account locked! Too many failed attempts. Please contact support."
        ok, msg = from_acc.withdraw(amount)
        if ok:
            to_acc.deposit(amount)
            log_transaction(from_acc.account_number, "TRANSFER_OUT", amount, from_acc.balance)
            log_transaction(to_acc.account_number, "TRANSFER_IN", amount, to_acc.balance)
            self.save_to_disk()
            return True,"Transfer Successful"
        return ok,msg
                        
    def get_active_accounts(self):
        accounts = []
        print("Active Accounts:")
        for acc in self.accounts.values():
            if acc.status == "Active":
                accounts.append(acc)         
        return accounts
    
    def get_inactive_accounts(self):
        accounts = []
        print("Inactive Accounts:")
        for acc in self.accounts.values():
            if acc.status == "Inactive":
                accounts.append(acc)         
        return accounts
    
    def get_locked_accounts(self):
        accounts = []
        print("Locked Accounts:")
        for acc in self.accounts.values():
            if acc.is_locked():
                accounts.append(acc)
        return accounts
    
    def update_pin(self, account_number, old_pin, new_pin):
        acc = self.get_account(account_number)
        if not acc:
            return False, "Account not Found"
        if acc.status != "Active":
            return False, "Account is not Active"
        if acc.is_locked():
            return False, "Account is locked"
        
        # Validate old PIN if set - continuous checking until correct or locked
        if acc.pin is not None:
            while acc.failed_attempts < acc.max_attempts:
                if old_pin == acc.pin:
                    # PIN is correct, reset failed attempts
                    acc.reset_failed_attempts()
                    self.save_to_disk()
                    break
                else:
                    # PIN is incorrect, increment failed attempts
                    acc.increment_failed_attempts()
                    self.save_to_disk()
                    remaining_attempts = acc.max_attempts - acc.failed_attempts
                    
                    if acc.is_locked():
                        return None, f"Account locked! Too many failed attempts. Please contact support."
                    else:
                        print(f"Invalid PIN. {remaining_attempts} attempts remaining.")
                        old_pin = int(input("Enter your old pin again: "))
            
            # If we exit the loop and still locked, return error
            if acc.is_locked():
                return None, f"Account locked! Too many failed attempts. Please contact support."
        
        acc.pin = new_pin
        acc.reset_failed_attempts()
        self.save_to_disk()
        return True, "PIN updated successfully"
    
    def change_account_type(self, account_number, new_type):
        acc = self.get_account(account_number)
        if not acc:
            return False, "Account not Found"
        if acc.status != "Active":
            return False, "Account is not Active"
        if acc.is_locked():
            return False, "Account is locked"
        new_type = new_type.title()
        if new_type not in Account.MIN_BALANCE:
            return False , f"Invalid Account type. Choose from {list(Account.MIN_BALANCE.keys())}"
        min_req = Account.MIN_BALANCE[new_type]
        if acc.balance < min_req:
            return False, f"Current balance is less than the minimum required balance for {new_type} account which is {min_req}"
        acc.account_type = new_type
        self.save_to_disk()
        return True, f"Account type changed successfully to {new_type}"
    
    def change_account_name(self, account_number, new_name):
        acc = self.get_account(account_number)
        if not acc:
            return False, "Account not Found"
        if acc.status != "Active":
            return False, "Account is not Active"
        if acc.is_locked():
            return False, "Account is locked"
        if not new_name.strip():
            return False, "Name cannot be empty"
        acc.name = new_name.strip()#remove leading and trailing spaces
        acc.name = " ".join(word.capitalize() for word in acc.name.split())#capitalize each word
        self.save_to_disk()
        return True, "Account holder's name updated successfully"
    
    def delete_account(self, account_number):
        acc = self.get_account(account_number)
        if not acc:
            return False, "Account not Found"
        del self.accounts[account_number]
        self.save_to_disk()
        return True, "Account deleted successfully"

    def fixed_deposit(self,account_number,amount,tenure,pin):
        acc = self.get_account(account_number)
        print(f"Account Balance: {acc.balance}")
        if amount <= 0:
            return False,"Amount must be positive"
        if amount > acc.balance:
            return False,"Insufficient balance for fixed deposit"
        if tenure < 1 or tenure > 10:
            return False,"Tenure must be between 1 and 10 years"
        if not acc:
            return False,"Account not Found"
        if acc.status != "Active":
            return False,"Account is not Active"
        if acc.is_locked():
            return False,"Account is locked"
        
        
        # Validate PIN if set - continuous checking until correct or locked
        if acc.pin is not None:
            while acc.failed_attempts < acc.max_attempts:
                if pin == acc.pin:
                    # PIN is correct, reset failed attempts
                    acc.reset_failed_attempts()
                    self.save_to_disk()
                    break
                else:
                    # PIN is incorrect, increment failed attempts
                    acc.increment_failed_attempts()
                    self.save_to_disk()
                    remaining_attempts = acc.max_attempts - acc.failed_attempts
                    
                    if acc.is_locked():
                        return None, f"Account locked! Too many failed attempts. Please contact support."
                    else:
                        print(f"Invalid PIN. {remaining_attempts} attempts remaining.")
                        pin = int(input("Enter your pin again: "))
            
            # If we exit the loop and still locked, return error
            if acc.is_locked():
                return None, f"Account locked! Too many failed attempts. Please contact support."
        
        
        # Interest calculation using simple interest formula
        rate_of_interest = 5.0  # Fixed interest rate of 5% per annum
        interest = (amount * rate_of_interest * tenure) / 100
        maturity_amount = amount + interest
        
        # Deduct the fixed deposit amount from the account balance
        acc.withdraw(amount)
        log_transaction(acc.account_number, "FIXED_DEPOSIT", amount, acc.balance)
        self.save_to_disk()
        
        statement = (
            f"\nFixed Deposit Created Successfully!\n"
            f"Principal Amount: {amount:.2f}\n"
            f"Tenure: {tenure} years\n"
            f"Rate of Interest: {rate_of_interest}% per annum\n"
            f"Interest Earned: {interest:.2f}\n"
            f"Maturity Amount: {maturity_amount:.2f}\n\n"
            f"Amount of {amount:.2f} has been deducted from your account.\n"
            f"New Account Balance: {acc.balance:.2f}\n"
            f"Amount matured after {tenure} years will be {maturity_amount:.2f}\n"
        )
        return True, statement
    
    
    def get_account_statement(self,account_number,pin):
        acc = self.get_account(account_number)
        if not acc:
            return False,"Account not Found"
        
        if acc.status != "Active":
            return False,"Account is not Active"
        
        if acc.is_locked():
            return False,"Account is locked"
        
        # Validate PIN if set - continuous checking until correct or locked
        if acc.pin is not None:
            while acc.failed_attempts < acc.max_attempts:
                if pin == acc.pin:
                    # PIN is correct, reset failed attempts
                    acc.reset_failed_attempts()
                    self.save_to_disk()
                    break
                else:
                    # PIN is incorrect, increment failed attempts
                    acc.increment_failed_attempts()
                    self.save_to_disk()
                    remaining_attempts = acc.max_attempts - acc.failed_attempts
                    
                    if acc.is_locked():
                        return None, f"Account locked! Too many failed attempts. Please contact support."
                    else:
                        print(f"Invalid PIN. {remaining_attempts} attempts remaining.")
                        pin = int(input("Enter your pin again: "))
            
            # If we exit the loop and still locked, return error
            if acc.is_locked():
                return None, f"Account locked! Too many failed attempts. Please contact support."
        
        all_transactions = load_transactions()
        # Filter transactions for the given account number (which is at index 1)
        account_transactions = [" | ".join(t) for t in all_transactions 
                                if t and len(t) > 1 and t[1] == str(account_number)]


        statement_header = [
            "----------------------------------",
            f"Account Statement for: {acc.name} ({acc.account_number})",
            f"Current Balance: {acc.balance:.2f}",
            "----------------------------------",
            "Timestamp | Account No | Operation | Amount | Balance After",
            "----------------------------------"
        ]

        if not account_transactions:
            statement_body = ["No transactions found for this account."]
        else:
            statement_body = account_transactions

        full_statement = "\n".join(statement_header + statement_body)
        return full_statement, "Statement generated successfully."
     
    def activate(self, account_number, pin):
        acc = self.get_account(account_number)
        if not acc:
            return False,"Account not found"
        if pin == acc.pin:
            acc.status = "Active"
            log_transaction(acc.account_number, "OPENED" , None, acc.balance)
            acc.reset_failed_attempts()
            self.save_to_disk()
            return True , "Account activated successfully\n\n"
        
    def get_transactions(self, account_number):
        """
        Retrieves all transactions for a specific account.
        1. Validates the account exists.
        2. Loads all transactions from the log file.
        3. Filters transactions belonging to the specified account number.
        4. Returns a list of formatted transaction strings.
        """
        acc = self.get_account(account_number)
        if not acc:
            return []  # Return an empty list if account not found
        all_transactions = load_transactions()
        account_transactions = [" | ".join(t) for t in all_transactions if t and len(t) > 1 and t[1] == str(account_number)]
        return account_transactions
    
    def unlock_account(self, account_number, pin):
        acc = self.get_account(account_number)
        if not acc:
            return False, "Account not Found"
        if acc.status == "Inactive":
            return False, "Account is not avtive. Please activate it first."
        if not acc.is_locked():
            return False, "Account is not locked."
        if pin != acc.pin:
            return False, "Invalid PIN. Cannot unlock account."
        log_transaction(account_number,"OPENED",None,acc.balance)
        acc.reset_failed_attempts()
        self.save_to_disk()
        return True,"Account unlocked successfully"

    def balance_inquiry(self, account_number):
        """Return the account and a formatted balance string for display.

        This does not change state; it only reads the balance.
        """
        acc = self.get_account(account_number)
        if not acc:
            return False, "Account not Found"
        return acc, f"Balance: {acc.balance: .2f}"
    
    def lend_loan(self,account_number):
        acc = self.get_account(account_number)
        if not acc:
            return False, "Account not Found"
        if acc.status != "Active":
            return False, "Account is not Active"
        if acc.account_type != "Savings":
            return False, "Only Savings account holders are eligible for loans."
        if acc.balance < 5000:
            return False, "Minimum balance of 5000 required to be eligible for a loan."
        loan_amount = acc.balance * 5
        print(f"You are eligible for a loan of up to {loan_amount:.2f}")
        print("Loan Terms:")
        print(" - Interest Rate: 2.5% per annum")
        print(" - Maximum Tenure: 5 years")

        intrested = input("Do you want to proceed with the loan application? (y/n): ").strip().lower()
        if intrested == 'n':
            return False, "Loan application cancelled."
        else:
            tenure = int(input("Enter loan tenure in years (max 5 years): "))
            if tenure < 1 or tenure > 5:
                return False, "Invalid tenure. Must be between 1 and 5 years."
            principal = float(input(f"Enter loan amount (max {loan_amount:.2f}): "))
            if principal <= 0 or principal > loan_amount:
                return False, f"Invalid loan amount. Must be between 0 and {loan_amount:.2f}."
            rate = 2.5
            n = tenure * 12
            r = rate / (12 * 100)
            emi = (principal * r * (1 + r)**n) / ((1 + r)**n - 1)
            total_payment = emi * n
            total_interest = total_payment - principal
            print(f"\nLoan Details:")
            print(f" - Principal Amount: {principal:.2f}")
            print(f" - Tenure: {tenure} years")
            print(f" - Monthly EMI: {emi:.2f}")
            print(f" - Total Payment (Principal + Interest): {total_payment:.2f}")
            print(f" - Total Interest Payable: {total_interest:.2f}\n")
            confirm = input("Do you want to accept this loan? (y/n): ").strip().lower()
            if confirm == 'y':
                acc.deposit(principal)
                log_transaction(acc.account_number, "LOAN_DISBURSED", principal, acc.balance)
                self.save_to_disk()
                return True, f"Loan of {principal:.2f} disbursed successfully. Amount credited to your account."
            else:
                return False, "Loan application cancelled."



    def close_account(self, account_number):
        """Mark an account as Inactive, log the change, and save.

        Steps:
        1) Fetch the account; error if missing.
        2) Set status to "Inactive" (does not delete the account).
        3) Log the CLOSE operation and persist the new state.
        """
        acc = self.get_account(account_number)
        if not acc:
           return False, "Account not Found"
         
        acc.status = "Inactive"
        log_transaction(acc.account_number, "CLOSE" , None, acc.balance)
        self.save_to_disk()
        return True , "Account closed successfully"