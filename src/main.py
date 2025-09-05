from services.banking_service import BankingService

def main():
    bank = BankingService()
    print("Welcome to GlobalDigital Bank")

    while True:
        print("\n--- Main Menu ---")
        print("1) Create Account")
        print("2) Deposit")
        print("3) Withdraw")
        print("4) Balance Inquiry")
        print("5) Close Account")
        print("6) Search by Name")
        print("7) Search by Account Number")
        print("8) List Active Accounts")
        print("9) List Closed Accounts")
        print("10) Reopen Account")
        print("11) Rename Account Holder")
        print("12) Delete All Accounts")
        print("13) Count Active Accounts")
        print("14) Exit")

        choice = input("Enter Choice: ")

        if choice == "1":
            name = input("Enter Name: ")
            age = input("Enter age: ")
            acc_type = input("Enter account type (Savings/Current): ")
            initial = input("Initial Deposit amount: ")
            acc, msg = bank.create_account(name, age, acc_type, initial)
            print(msg)
            if acc:
                print(acc)

        elif choice == "2":
            acc_no = input("Enter account number: ")
            amount = input("Enter amount to deposit: ")
            ok, msg = bank.deposit(acc_no, amount)
            print(msg)

        elif choice == "3":
            acc_no = input("Enter your account number: ")
            amount = input("Enter amount to withdraw: ")
            ok, msg = bank.withdraw(acc_no, amount)
            print(msg)

        elif choice == "4":
            acc_no = input("Enter Account Number: ")
            acc, msg = bank.balance_inquiry(acc_no)
            print(acc if acc else msg)

        elif choice == "5":
            acc_no = input("Enter account number to close: ")
            ok, msg = bank.close_account(acc_no)
            print(msg)

        elif choice == "6":
            print("Thank you for visiting GlobalDigital Bank")
            break

        elif choice == "7":
            name = input("Enter name to search: ")
            results, msg = bank.search_by_name(name)
            if results:
                for acc in results:
                    print(acc)
            else:
                print(msg)

        elif choice == "8":
            acc_no = input("Enter account number to search: ")
            acc, msg = bank.search_by_account_number(acc_no)
            if acc:
                print(acc)
            else:
                print(msg)

        elif choice == "9":
            accounts, msg = bank.list_active_accounts()
            print(msg)
            for acc in accounts:
                print(acc)

        elif choice == "10":
            accounts, msg = bank.list_closed_accounts()
            print(msg)
            for acc in accounts:
                print(acc)

        elif choice == "11":
            acc_no = input("Enter account number to reopen: ")
            ok, msg = bank.reopen_account(acc_no)
            print(msg)

        elif choice == "12":
            acc_no = input("Enter account number: ")
            new_name = input("Enter new name: ")
            ok, msg = bank.rename_account_holder(acc_no, new_name)
            print(msg)

        elif choice == "13":
            confirm = input("Are you sure you want to delete all accounts? (yes/no): ")
            if confirm.lower() == 'yes':
                ok, msg = bank.delete_all_accounts()
                print(msg)
            else:
                print("Operation cancelled")

        elif choice == "14":
            count, msg = bank.count_active_accounts()
            print(msg)

        elif choice == "15":
            print("Thank you for visiting GlobalDigital Bank")
            break

        else:
            print("Invalid Choice.\n Try Again!!")

if __name__ == "__main__":
    main()
        
            