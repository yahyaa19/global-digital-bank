from services.banking_services import BankingService

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
        print("8) List All Active Accounts")
        print("9) List All Closed Accounts")
        print("10) Reopen Closed Account")
        print("11) Rename Account Holder")
        print("12) Delete All Accounts")
        print("13) Count Active Accounts")
        print("14) View Transaction History (per account)")
        print("15) Transfer Funds (between accounts)")
        print("16) Show Today's Transaction Total (per account)")
        print("17) Top N Accounts by Balance")
        print("18) Average Balance Calculator")
        print("19) Youngest Account Holder")
        print("20) Oldest Account Holder")
        print("21) Simple Interest Calculator")
        print("0) Exit")

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
            name = input("Enter name to search: ")
            results = bank.search_by_name(name)
            if results:
                for acc in results:
                    print(acc)
            else:
                print("No account found with that name.")

        elif choice == "7":
            acc_no = input("Enter account number to search: ")
            acc = bank.search_by_account_number(acc_no)
            print(acc if acc else "Account not found.")

        elif choice == "8":
            active_accounts = bank.list_active_accounts()
            if active_accounts:
                for acc in active_accounts:
                    print(acc)
            else:
                print("No active accounts.")

        elif choice == "9":
            closed_accounts = bank.list_closed_accounts()
            if closed_accounts:
                for acc in closed_accounts:
                    print(acc)
            else:
                print("No closed accounts.")

        elif choice == "10":
            acc_no = input("Enter account number to reopen: ")
            ok, msg = bank.reopen_closed_account(acc_no)
            print(msg)

        elif choice == "11":
            acc_no = input("Enter account number to rename: ")
            new_name = input("Enter new account holder name: ")
            ok, msg = bank.rename_account_holder(acc_no, new_name)
            print(msg)

        elif choice == "12":
            confirm = input("Are you sure you want to delete all accounts? Type YES to confirm: ")
            if confirm == "YES":
                ok, msg = bank.delete_all_accounts()
                print(msg)
            else:
                print("Operation cancelled.")

        elif choice == "13":
            count = bank.count_active_accounts()
            print(f"Active accounts count: {count}")

        elif choice == "14":
            acc_no = input("Enter account number to view history: ")
            history = bank.get_transaction_history(acc_no)
            if history:
                print("\nTransaction History:")
                for entry in history:
                    print(entry)
            else:
                print("No transactions found for this account.")

        elif choice == "15":
            from_acc = input("Enter sender account number: ")
            to_acc = input("Enter receiver account number: ")
            amount = input("Enter amount to transfer: ")
            ok, msg = bank.transfer_funds(from_acc, to_acc, amount)
            print(msg)

        elif choice == "16":
            acc_no = input("Enter account number: ")
            total = bank.get_today_total(acc_no)
            print(f"Today's transaction total for account {acc_no}: {total}")

        elif choice == "17":
            n = input("Enter N (number of top accounts): ")
            try:
                n = int(n)
            except:
                n = 5
            top_accounts = bank.top_n_accounts_by_balance(n)
            print(f"Top {n} Accounts by Balance:")
            for acc in top_accounts:
                print(acc)

        elif choice == "18":
            avg = bank.average_balance()
            print(f"Average balance (active accounts): {avg}")

        elif choice == "19":
            acc = bank.youngest_account_holder()
            print(acc if acc else "No active accounts.")

        elif choice == "20":
            acc = bank.oldest_account_holder()
            print(acc if acc else "No active accounts.")

        elif choice == "21":
            acc_no = input("Enter account number: ")
            rate = input("Enter annual interest rate (%): ")
            years = input("Enter number of years: ")
            interest, msg = bank.simple_interest(acc_no, rate, years)
            print(msg)

        elif choice == "0":
            print("Thank you for visiting GlobalDigital Bank")
            break

        else:
            print("Invalid Choice.\n Try Again!!")

if __name__ == "__main__":
    main()
        
            