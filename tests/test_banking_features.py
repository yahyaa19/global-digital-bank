#!/usr/bin/env python3
"""
Comprehensive test suite for Global Digital Bank System
Tests all features F1-F24
"""

import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))

from services.banking_service import BankingService
from models.account import Account
import tempfile
import csv

def test_basic_operations():
    """Test basic banking operations"""
    print("Testing Basic Operations...")
    bank = BankingService()
    
    # Test account creation with age verification (F19)
    acc, msg = bank.create_account("John Doe", "25", "Savings", "1000")
    assert acc is not None, f"Account creation failed: {msg}"
    print(f"✓ Account created: {acc.account_number}")
    
    # Test underage account creation
    acc_underage, msg_underage = bank.create_account("Minor", "17", "Savings", "1000")
    assert acc_underage is None, "Underage account should be rejected"
    print("✓ Underage account properly rejected")
    
    # Test deposit
    ok, msg = bank.deposit(acc.account_number, "500")
    assert ok, f"Deposit failed: {msg}"
    print("✓ Deposit successful")
    
    # Test withdrawal with minimum balance check (F8)
    ok, msg = bank.withdraw(acc.account_number, "100")
    assert ok, f"Withdrawal failed: {msg}"
    print("✓ Withdrawal successful")
    
    # Test minimum balance enforcement
    ok, msg = bank.withdraw(acc.account_number, "2000")
    assert not ok, "Should not allow withdrawal below minimum balance"
    print("✓ Minimum balance check working")
    
    return bank, acc

def test_search_features(bank, test_acc):
    """Test search features F1, F7"""
    print("\nTesting Search Features...")
    
    # Test search by name (F1)
    results, msg = bank.search_by_name("John")
    assert len(results) > 0, "Search by name failed"
    print("✓ Search by name working")
    
    # Test search by account number (F7)
    acc, msg = bank.search_by_account_number(test_acc.account_number)
    assert acc is not None, "Search by account number failed"
    print("✓ Search by account number working")

def test_account_management(bank, test_acc):
    """Test account management features F2, F3, F4, F5"""
    print("\nTesting Account Management...")
    
    # Test list active accounts (F2)
    active_accounts, msg = bank.list_active_accounts()
    assert len(active_accounts) > 0, "List active accounts failed"
    print("✓ List active accounts working")
    
    # Test account type upgrade (F4)
    ok, msg = bank.upgrade_account_type(test_acc.account_number, "Current")
    assert ok, f"Account upgrade failed: {msg}"
    print("✓ Account type upgrade working")
    
    # Test close account
    ok, msg = bank.close_account(test_acc.account_number)
    assert ok, f"Close account failed: {msg}"
    print("✓ Close account working")
    
    # Test list closed accounts (F3)
    closed_accounts, msg = bank.list_closed_accounts()
    assert len(closed_accounts) > 0, "List closed accounts failed"
    print("✓ List closed accounts working")
    
    # Test reopen account (F5)
    ok, msg = bank.reopen_account(test_acc.account_number)
    assert ok, f"Reopen account failed: {msg}"
    print("✓ Reopen account working")

def test_financial_features(bank, test_acc):
    """Test financial features F9, F10, F11, F12, F13"""
    print("\nTesting Financial Features...")
    
    # Create second account for transfer testing
    acc2, msg = bank.create_account("Jane Smith", "30", "Current", "2000")
    assert acc2 is not None, "Second account creation failed"
    
    # Test transfer funds (F11)
    ok, msg = bank.transfer_funds(acc2.account_number, test_acc.account_number, "200")
    assert ok, f"Transfer failed: {msg}"
    print("✓ Transfer funds working")
    
    # Test transaction history (F12)
    transactions, msg = bank.get_transaction_history(test_acc.account_number)
    assert len(transactions) > 0, "Transaction history failed"
    print("✓ Transaction history working")
    
    # Test simple interest calculator (F9)
    result, msg = bank.calculate_simple_interest(test_acc.account_number, "2")
    assert result is not None, f"Interest calculation failed: {msg}"
    print("✓ Simple interest calculator working")
    
    # Test average balance calculator (F13)
    avg_balance, msg = bank.calculate_average_balance()
    assert avg_balance > 0, "Average balance calculation failed"
    print("✓ Average balance calculator working")
    
    return acc2

def test_analytics_features(bank):
    """Test analytics features F14, F15, F16, F21"""
    print("\nTesting Analytics Features...")
    
    # Test youngest account holder (F14)
    youngest, msg = bank.get_youngest_account_holder()
    assert youngest is not None, "Get youngest account holder failed"
    print("✓ Youngest account holder working")
    
    # Test oldest account holder (F15)
    oldest, msg = bank.get_oldest_account_holder()
    assert oldest is not None, "Get oldest account holder failed"
    print("✓ Oldest account holder working")
    
    # Test top accounts by balance (F16)
    top_accounts, msg = bank.get_top_accounts_by_balance(3)
    assert len(top_accounts) > 0, "Top accounts by balance failed"
    print("✓ Top accounts by balance working")
    
    # Test count active accounts (F21)
    count, msg = bank.count_active_accounts()
    assert count > 0, "Count active accounts failed"
    print("✓ Count active accounts working")

def test_security_features(bank, test_acc):
    """Test security features F17"""
    print("\nTesting Security Features...")
    
    # Test set PIN (F17)
    ok, msg = bank.set_pin(test_acc.account_number, "1234")
    assert ok, f"Set PIN failed: {msg}"
    print("✓ Set PIN working")
    
    # Test verify PIN
    ok, msg = bank.verify_pin(test_acc.account_number, "1234")
    assert ok, f"Verify PIN failed: {msg}"
    print("✓ Verify PIN working")
    
    # Test change PIN
    ok, msg = bank.change_pin(test_acc.account_number, "1234", "5678")
    assert ok, f"Change PIN failed: {msg}"
    print("✓ Change PIN working")

def test_data_management(bank):
    """Test data management features F18, F22, F23, F24"""
    print("\nTesting Data Management...")
    
    # Test export accounts (F18)
    with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
        export_file = f.name
    
    ok, msg = bank.export_accounts(export_file)
    assert ok, f"Export accounts failed: {msg}"
    print("✓ Export accounts working")
    
    # Test import accounts (F24)
    # Create a test import file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
        import_file = f.name
        writer = csv.writer(f)
        writer.writerow(["Account Number", "Name", "Age", "Account Type", "Balance", "Status"])
        writer.writerow(["9999", "Test Import", "25", "Savings", "1500.00", "Active"])
    
    ok, msg = bank.import_accounts(import_file)
    assert ok, f"Import accounts failed: {msg}"
    print("✓ Import accounts working")
    
    # Test safe exit (F23)
    ok, msg = bank.safe_exit()
    assert ok, f"Safe exit failed: {msg}"
    print("✓ Safe exit working")
    
    # Clean up temp files
    os.unlink(export_file)
    os.unlink(import_file)

def run_all_tests():
    """Run all test suites"""
    print("=" * 50)
    print("GLOBAL DIGITAL BANK - COMPREHENSIVE TEST SUITE")
    print("Testing Features F1-F24")
    print("=" * 50)
    
    try:
        # Test basic operations
        bank, test_acc = test_basic_operations()
        
        # Test search features
        test_search_features(bank, test_acc)
        
        # Test account management
        test_account_management(bank, test_acc)
        
        # Test financial features
        test_acc2 = test_financial_features(bank, test_acc)
        
        # Test analytics features
        test_analytics_features(bank)
        
        # Test security features
        test_security_features(bank, test_acc)
        
        # Test data management
        test_data_management(bank)
        
        print("\n" + "=" * 50)
        print("🎉 ALL TESTS PASSED! 🎉")
        print("All features F1-F24 are working correctly!")
        print("=" * 50)
        
    except AssertionError as e:
        print(f"\n❌ TEST FAILED: {e}")
        return False
    except Exception as e:
        print(f"\n💥 UNEXPECTED ERROR: {e}")
        return False
    
    return True

if __name__ == "__main__":
    run_all_tests()
