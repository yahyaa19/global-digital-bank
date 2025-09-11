from services.banking_services import BankingService
import random,sys

def again():
        msg = input("If you need any other Global bank service?? \nIf yes enter yes if not enter no or just press enter\n")
        if msg.lower()== "yes":
            main()
        elif msg.lower()=="no" or msg.lower()=="":
            sys.exit()
        else:
            print("invalid input")

def main_menu():
    main()

menu_structure = {
    "1. Account Management": [
        "Create a new account",
        "Close an account",
        "Activate account",
        "Unlock account"
    ],
    "2. Fund Operation": [
        "Deposit money",
        "Withdraw money",
        "Money Transfer"
    ],
    "3. Search & Reports": [
        "Check balance (Search by account number)",
        "Get account statement",
        "View transactions for an account"
    ],
    "4. Admin Section": [
        "Search by name",
        "List all active accounts",
        "List all inactive accounts",
        "List all locked accounts",
        "Updated pin for an account",
        "Change the account type",
        "Change the account holder's name",
        "Delete an account"
    ],
    "5. Loan Services": [],
    "6. Fixed Deposit": [],
    "7. Exit": []
}

def print_menu(menu, indent=0):
    for key, subitems in menu.items():
        print(" " * indent + key)
        for item in subitems:
            print(" " * (indent + 4) + "- " + item)
        print("-" * 60)     
    
  
def main():
    
    while True:
        banking_service = BankingService()
        print("\nWelcome to the Global Digital Bank!")
        print("\n------------------------ Main Menu --------------------------\n")
        print_menu(menu_structure)

        choice = input("\nEnter your choice: ")

        if choice == "1":
            print("\n--- Account Management ---")
            print("-"*25)
            print("1. Create a new account")
            print("2. Close an account")
            print("3. Activate account")
            print("4. Unlock account")
            print("5. Go Back to Main Menu\n")
            print("-"*25+"\n")
            sub_choice = input("Enter your choice: ")

            if sub_choice == "1":
                name = input("Enter your name: ")
                age = int(input("Enter your age: "))
                account_type = input("Enter your account type: ")
                initial_deposit = float(input("Enter your initial deposit: "))
                choice_pin = input("do you want to set a pin? (y/n): ")
                
                while True:
                    if choice_pin.lower() == "y":
                        pin = input("enter your pin: ")
                        break
                    elif choice_pin.lower() == "n":
                        print("pin not set,so random pin is generated")
                        pin = random.randint(1000, 9999)
                        print(f"Your generated pin is: {pin}")
                        break
                    else:
                        print("Invalid choice\n please enter y or n")
                        choice_pin = input("do you want to set a pin? (y/n): ")
                        
                acc, msg = banking_service.create_account(name, age, account_type, initial_deposit, pin)
                print(msg)
                if acc:
                    print(acc)
                again()

            elif sub_choice == "2":
                acc_no = int(input("Enter your account number: "))
                ok, msg = banking_service.close_account(acc_no)
                print(msg)
                again()

            elif sub_choice == "3":
                acc_no = int(input("Enter your account number: "))
                # Check if account exists and is already active before asking for PIN
                acc, msg = banking_service.balance_inquiry(acc_no)
                if not acc:
                    print(msg)
                    again()
                    continue
                if acc.status == "Active":
                    print("Account is already active")
                    again()
                    continue
                pin = int(input("Enter your pin to activate: "))
                ok, msg = banking_service.activate(acc_no, pin)
                print(msg)
                again()

            elif sub_choice == "4":
                acc_no = int(input("Enter your account number: "))
                pin = int(input("Enter your pin: "))
                ok, msg = banking_service.unlock_account(acc_no, pin)
                print(msg)
                again()
            
            elif sub_choice == "5":
                main_menu()

            else:
                print("Invalid choice.")
                again()

        elif choice == "2":
            print("\n--- Fund Operation ---")
            print("-"*25)
            print("1. Deposit money")
            print("2. Withdraw money")
            print("3. Money Transfer")
            print("4. Go Back to Main Menu")
            print("-"*25+"\n")
            sub_choice = input("Enter your choice: ")

            if sub_choice == "1":
                acc_no = int(input("Enter your account number: "))
                amount = float(input("Enter the amount to deposit: "))
                pin = int(input("Enter your pin: "))
                ok, msg = banking_service.deposit(acc_no, amount, pin)
                print(msg)
                again()

            elif sub_choice == "2":
                acc_no = int(input("Enter your account number: "))
                amount = float(input("Enter the amount to withdraw: "))
                pin = int(input("Enter your pin: "))
                ok, msg = banking_service.withdraw(acc_no, amount, pin)
                print(msg)
                again()

            elif sub_choice == "3":
                from_acc_no = int(input("Enter your account number: "))
                to_acc_no = int(input("Enter the recipient's account number: "))
                amount = float(input("Enter the amount to transfer: "))
                pin = int(input("Enter your pin: "))
                ok, msg = banking_service.transfer(from_acc_no, to_acc_no, pin, amount)
                print(msg)
                again()

            elif sub_choice == "4":
                main_menu()

            else:
                print("Invalid choice.")
                again()

        elif choice == "3":
            print("\n--- Search & Reports ---")
            print("-"*25)
            print("1. Check balance (Search by account number)")
            print("2. Get account statement")
            print("3. View transactions for an account")
            print("4. Go Back to Main Menu")
            print("-"*25+"\n")
            sub_choice = input("Enter your choice: ")

            if sub_choice == "1":
                acc_no = int(input("Enter your account number: "))
                acc, msg = banking_service.balance_inquiry(acc_no)
                print(msg)
                if acc:
                    print(acc)
                again()

            elif sub_choice == "2":
                acc_no = int(input("Enter the account number: "))
                pin = int(input("Enter the pin: "))
                acc, msg = banking_service.get_account_statement(acc_no, pin)
                print(msg)
                if acc:
                    print(acc)
                again()
                
            elif sub_choice == "3":
                account_number = int(input("Enter the account number: "))
                transactions = banking_service.get_transactions(account_number)
                if transactions:
                    for transaction in transactions:
                        print(transaction)
                else:
                    print("No transactions found.")
                again()

            elif sub_choice == "4":
                main_menu()

            else:
                print("Invalid choice.")
                again()

        elif choice == "4":
            print("\n--- Admin Section ---")
            print("-"*25)
            print("1. Search by name")
            print("2. List all active accounts")
            print("3. List all inactive accounts")
            print("4. List all locked accounts")
            print("5. Updated pin for an account")
            print("6. Change the account type")
            print("7. Change the account holder's name")
            print("8. Delete an account")
            print("9. Go Back to Main Menu")
            print("-"*25+"\n")
            sub_choice = input("Enter your choice: ")

            admin_pass = input("Enter admin password: ")
            if admin_pass != "admin123":
                print("Incorrect password.")
                again()
                continue

            if sub_choice == "1":
                name = input("Enter account holder's name: ")
                acc = banking_service.get_account_by_name(name)
                if acc:
                    print(acc)
                else:
                    print("Account not found.")
                again()

            elif sub_choice == "2":
                active_accounts = banking_service.get_active_accounts()
                if active_accounts:
                    for account in active_accounts:
                        print(account)
                else:
                    print("No active accounts found.")
                again()

            elif sub_choice == "3":
                inactive_accounts = banking_service.get_inactive_accounts()
                if inactive_accounts:
                    for account in inactive_accounts:
                        print(account)
                else:
                    print("No inactive accounts found.")
                again()

            elif sub_choice == "4":
                locked_accounts = banking_service.get_locked_accounts()
                if locked_accounts:
                    for account in locked_accounts:
                        print(account)
                else:
                    print("No locked accounts found.")
                again()

            elif sub_choice == "5":
                acc_no = int(input("Enter the account number: "))
                pin = int(input("Enter the old pin: "))
                new_pin = int(input("Enter the new pin: "))
                ok, msg = banking_service.update_pin(acc_no, pin, new_pin)
                print(msg)
                again()

            elif sub_choice == "6":
                acc_no = int(input("Enter the account number: "))
                new_type = input("Enter the new account type: ")
                ok, msg = banking_service.change_account_type(acc_no, new_type)
                print(msg)
                again()

            elif sub_choice == "7":
                acc_no = int(input("Enter the account number: "))
                new_name = input("Enter the new account holder's name: ")
                ok, msg = banking_service.change_account_holder_name(acc_no, new_name)
                print(msg)
                again()

            elif sub_choice == "8":
                acc_no = int(input("Enter the account number to delete: "))
                ok, msg = banking_service.delete_account(acc_no)
                print(msg)
                again()

            elif sub_choice == "9":
                main_menu()
                again()

            else:
                print("Invalid choice.")
                again()

        elif choice == "5":
            acc_no = int(input("Enter your account number: "))
            ok, msg = banking_service.lend_loan(acc_no)
            print(msg)
            again()

        elif choice == "6":
            print("Interest rate is 5% per annum.\n"
              "Maturity amount will be calculated using simple interest formula.")
            acc = int(input("Enter your account number: "))
            amount = float(input("Enter the amount for fixed deposit: "))
            tenure = int(input("Enter the tenure in years: "))
            pin = int(input("Enter your pin: "))
            ok, msg = banking_service.fixed_deposit(acc, amount, tenure, pin)
            print(msg)
            again()



        elif choice == "7":
            print("Thank you for using Global Digital Bank. Goodbye!")
            sys.exit()


        else:
            print("Invalid choice")

if __name__ == "__main__":
    main()