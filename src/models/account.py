import random
class Account:
    MIN_BALANCE = {"Savings": 500, "Current": 1000}
    MAX_SINGLE_DEPOSIT = 100000.0

    def __init__(self, 
                 account_number, 
                 name, 
                 age, 
                 account_type,
                 balance = 0.0,
                 status = "Active",
                 pin = None,
                 locked = False,
                 failed_attempts = 0):
        
        self.account_number = int(account_number)
        self.name = name.strip()
        self.age = int(age)
        self.account_type = account_type.title()
        if self.account_type not in Account.MIN_BALANCE:
            raise ValueError(f"Invalid account type: {self.account_type}")
        self.balance = balance
        self.pin = pin
        self.status = status
        self.failed_attempts = int(failed_attempts)
        self.max_attempts = 3

    def reset_failed_attempts(self):
        """Reset failed attempts counter when PIN is entered correctly"""
        self.failed_attempts = 0

    def increment_failed_attempts(self):
        """Increment failed attempts counter"""
        self.failed_attempts += 1

    def is_locked(self):
        """Check if account is locked due to too many failed attempts"""
        return self.failed_attempts >= self.max_attempts
    
    def deposit(self, amount):
        try:
            amount = float(amount)
        except (TypeError, ValueError):
            return False, "Invalid Amount"
        
        if self.status != "Active":
            return False, "Account is inactive"

        if amount <= 0:
            return False, "Deposit must be positive"
        if amount >  Account.MAX_SINGLE_DEPOSIT:
            return False, f"Deposit exceeds single-deposit limit {Account.MAX_SINGLE_DEPOSIT}"
        
        self.balance += amount

        return True, f"Deposit Successful.\nNew Balance: {self.balance}"
    

    def withdraw(self, amount):
        try:
            amount = float(amount)
        except (TypeError, ValueError):
            return False, "Invalid Amount"
        
        if self.status != "Active":
            return False, "Account is inactive"
        if amount <= 0:
            return False, "Withdrawal must be positive"
        
        min_required = Account.MIN_BALANCE[self.account_type]
        if self.balance - amount < min_required:
            return False, f"Insufficient funds. Minimum required balance for {self.account_type}: {min_required}"

        self.balance -= amount
        return True, f"Withdrawal successful.\nNew Balance: {self.balance}"
    

    def to_dict(self):
        return {
            "account_number": self.account_number,
            "name": self.name,
            "age": self.age,
            "balance": self.balance,
            "account_type": self.account_type,
            "status": self.status,
            "pin": self.pin if self.pin else "",
            "failed_attempts": self.failed_attempts,
            "locked": self.is_locked()
        }
    
    def __str__(self):
        return f"[{self.account_number}] {self.name} ({self.account_type}) - Balance: {self.balance} - {self.status}"