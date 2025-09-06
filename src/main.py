
from services.banking_service import BankingService


def main():
    bank = BankingService()
    print("Welcome to GlobalDigital Bank")
    print("=== Complete Banking System with All Features ===")

    while True:
        print("\n--- Main Menu ---")
        print("Basic Operations:")

        print("1) Create Account")
        print("2) Deposit")
        print("3) Withdraw")
        print("4) Balance Inquiry")
        print("5) Close Account")
        print("6) Exit with Autosave (F23)")

        print("\nSearch & Account Management:")
        print("7) Search by Name (F1)")
        print("8) Search by Account Number (F7)")
        print("9) List Active Accounts (F2)")
        print("10) List Closed Accounts (F3)")
        print("11) Reopen Account (F5)")
        print("12) Rename Account Holder (F20)")
        print("13) Account Type Upgrade (F4)")

        print("\nTransaction & Financial Features:")
        print("14) Transfer Funds (F11)")
        print("15) Transaction History (F12)")
        print("16) Simple Interest Calculator (F9)")
        print("17) Average Balance Calculator (F13)")

        print("\nAccount Analytics:")
        print("18) Youngest Account Holder (F14)")
        print("19) Oldest Account Holder (F15)")
        print("20) Top N Accounts by Balance (F16)")
        print("21) Count Active Accounts (F21)")

        print("\nSecurity & Data Management:")
        print("22) Set/Change PIN (F17)")
        print("23) Export Accounts to File (F18)")
        print("24) Import Accounts from File (F24)")
        print("25) Delete All Accounts (F22)")



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

            # Exit with autosave
            ok, msg = bank.safe_exit()
            print(msg)
            if ok:
                print("Thank you for visiting GlobalDigital Bank")
                break
            else:
                print("Please try again or contact support.")

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
            # Account Type Upgrade
            acc_no = input("Enter account number: ")
            new_type = input("Enter new account type (Savings/Current): ")
            ok, msg = bank.upgrade_account_type(acc_no, new_type)
            print(msg)

        elif choice == "14":
            # Transfer Funds
            from_acc = input("Enter source account number: ")
            to_acc = input("Enter destination account number: ")
            amount = input("Enter amount to transfer: ")
            ok, msg = bank.transfer_funds(from_acc, to_acc, amount)
            print(msg)

        elif choice == "15":
            # Transaction History
            acc_no = input("Enter account number: ")
            transactions, msg = bank.get_transaction_history(acc_no)
            print(msg)
            if transactions:
                print("\n--- Transaction History ---")
                for trans in transactions:
                    details = f" - {trans['details']}" if trans['details'] else ""
                    print(f"{trans['timestamp']} | {trans['operation']} | Amount: {trans['amount']} | Balance: {trans['balance_after']}{details}")

        elif choice == "16":
            # Simple Interest Calculator
            acc_no = input("Enter account number: ")
            years = input("Enter time period in years (default 1): ") or "1"
            result, msg = bank.calculate_simple_interest(acc_no, years)
            print(msg)
            if result:
                print(f"\n--- Interest Calculation ---")
                print(f"Principal Amount: {result['principal']:.2f}")
                print(f"Interest Rate: {result['interest_rate']*100:.1f}% per annum")
                print(f"Time Period: {result['time_years']} year(s)")
                print(f"Interest Earned: {result['interest_earned']:.2f}")
                print(f"Total Amount: {result['total_amount']:.2f}")

        elif choice == "17":
            # Average Balance Calculator
            avg_balance, msg = bank.calculate_average_balance()
            print(msg)

        elif choice == "18":
            # Youngest Account Holder
            youngest, msg = bank.get_youngest_account_holder()
            print(msg)
            if youngest:
                print(youngest)

        elif choice == "19":
            # Oldest Account Holder
            oldest, msg = bank.get_oldest_account_holder()
            print(msg)
            if oldest:
                print(oldest)

        elif choice == "20":
            # Top N Accounts by Balance
            n = input("Enter number of top accounts to display (default 5): ") or "5"
            top_accounts, msg = bank.get_top_accounts_by_balance(n)
            print(msg)
            if top_accounts:
                print("\n--- Top Accounts by Balance ---")
                for i, acc in enumerate(top_accounts, 1):
                    print(f"{i}. {acc}")

        elif choice == "21":
            # Count Active Accounts
            count, msg = bank.count_active_accounts()
            print(msg)

        elif choice == "22":
            # Set/Change PIN
            acc_no = input("Enter account number: ")
            acc = bank.get_account(acc_no)
            if not acc:
                print("Account not found")
            elif acc.pin:
                # Change PIN
                old_pin = input("Enter current PIN: ")
                new_pin = input("Enter new PIN (4 digits): ")
                ok, msg = bank.change_pin(acc_no, old_pin, new_pin)
                print(msg)
            else:
                # Set PIN
                pin = input("Enter new PIN (4 digits): ")
                ok, msg = bank.set_pin(acc_no, pin)
                print(msg)

        elif choice == "23":
            # Export Accounts
            filename = input("Enter filename (press Enter for auto-generated): ").strip()
            if not filename:
                filename = None
            ok, msg = bank.export_accounts(filename)
            print(msg)

        elif choice == "24":
            # Import Accounts
            filename = input("Enter filename to import from: ")
            ok, msg = bank.import_accounts(filename)
            print(msg)

        elif choice == "25":
            # Delete All Accounts
            confirm = input("Are you sure you want to delete all accounts? (yes/no): ")
            if confirm.lower() == 'yes':
                ok, msg = bank.delete_all_accounts()
                print(msg)
            else:
                print("Operation cancelled")


        else:
            print("Invalid Choice.\n Try Again!!")

if __name__ == "__main__":
    main()
        
            