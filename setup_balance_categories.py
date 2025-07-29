#!/usr/bin/env python3
"""
Script to set up balance adjustment categories for the financial tracking app.
This ensures proper categorization when account balances are updated.
"""

import requests
import json

# Configuration
API_BASE_URL = "http://localhost:8085"  # Qurtesy Finance API port

def create_category(section, value, emoji):
    """Create a category via the API"""
    url = f"{API_BASE_URL}/api/categories/"
    
    # First, check if category already exists
    try:
        check_response = requests.get(f"{url}?section={section}")
        if check_response.status_code == 200:
            existing_categories = check_response.json()
            for cat in existing_categories:
                if cat['value'] == value:
                    print(f"✓ Category '{value}' already exists in {section}")
                    return cat
    except Exception as e:
        print(f"Warning: Could not check existing categories: {e}")
    
    # Create new category
    try:
        response = requests.post(
            url,
            params={"section": section},
            json={"value": value, "emoji": emoji}
        )
        
        if response.status_code == 200:
            category = response.json()
            print(f"✓ Created category: {emoji} {value} ({section})")
            return category
        else:
            print(f"✗ Failed to create category '{value}': {response.text}")
            return None
            
    except Exception as e:
        print(f"✗ Error creating category '{value}': {e}")
        return None

def main():
    """Set up balance adjustment categories"""
    print("🏦 Setting up Balance Adjustment Categories for Qurtesy Finance")
    print("=" * 60)
    
    categories_to_create = [
        # Income categories for positive balance adjustments
        ("INCOME", "Salary", "💰"),
        ("INCOME", "Income Adjustment", "⚖️"),
        ("INCOME", "Interest Earned", "📈"),
        ("INCOME", "Refund", "💸"),
        
        # Expense categories for negative balance adjustments
        ("EXPENSE", "Dining", "🍽"),
        ("EXPENSE", "Groceries", "🛒"),
        ("EXPENSE", "Shopping", "🛍️"),
        ("EXPENSE", "Transit", "🚌"),
        ("EXPENSE", "Entertainment", "📻"),
        ("EXPENSE", "Bills & Fees", "💸"),
        ("EXPENSE", "Gifts", "🎁"),
        ("EXPENSE", "Beauty", "🌼"),
        ("EXPENSE", "Work", "💼"),
        ("EXPENSE", "Travel", "✈️"),
        ("EXPENSE", "Expense Adjustment", "⚖️"),

        ("TRANSFER", "Transfer (Default)", "🔀"),
    ]
    
    created_categories = []
    
    for section, value, emoji in categories_to_create:
        category = create_category(section, value, emoji)
        if category:
            created_categories.append(category)
    
    print("\n" + "=" * 60)
    print(f"🎉 Setup complete! Created {len(created_categories)} categories.")
    print("\nRecommended usage:")
    print("• 'Balance Adjustment' - General balance corrections")
    print("• 'Account Reconciliation' - Matching bank statements")
    print("• 'Found Money/Bank Fees' - Specific adjustments")
    print("• 'Interest Earned/ATM Charges' - Bank-related changes")
    
    print("\n💡 Next steps:")
    print("1. Start your backend server if not running")
    print("2. Test the balance adjustment feature in Account Settings")
    print("3. Update an account balance to see automatic transaction creation")

if __name__ == "__main__":
    main()
