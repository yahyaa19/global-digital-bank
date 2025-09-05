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
        print("6) Exit")
        print("7) Search by Name")

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

        else:
            print("Invalid Choice.\n Try Again!!")

if __name__ == "__main__":
    main()
        
            