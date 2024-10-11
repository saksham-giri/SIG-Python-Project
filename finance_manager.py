import json
from datetime import datetime
import pandas as pd
import matplotlib.pyplot as plt


class User:
    def __init__(self, username, password):
        self.username = username
        self.password = password


def load_users():
    try:
        with open('users.json', 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return {}

def save_users(users):
    with open('users.json', 'w') as f:
        json.dump(users, f)

def register_user():
    users = load_users()
    username = input("enter a username: ")
    if username in users:
        print("Username already exists")
        return None
    password = input("enter password: ")
    users[username] = password
    save_users(users)
    return User(username, password)

def login_user():
    users = load_users()
    username = input("Enter username: ")
    password = input("Enter password: ")
    if username in users and users[username] == password:
        return User(username, password)
    else:
        print("wrong username or password.")
        return None


class FinanceRecord:
    def __init__(self, description, amount, category, date):
        self.description = description
        self.amount = amount
        self.category = category
        self.date = date

    def to_dict(self):
        return {
            'description': self.description,
            'amount': self.amount,
            'category': self.category,
            'date': self.date.isoformat()
        }

    @classmethod
    def from_dict(cls, data):
        return cls(
            data['description'],
            data['amount'],
            data['category'],
            datetime.fromisoformat(data['date'])
        )


class FinanceManager:
    def __init__(self, user):
        self.user = user
        self.records = self.load_records()

    def load_records(self):
        try:
            with open('finances.json', 'r') as f:
                data = json.load(f)
                if self.user.username in data:
                    return [FinanceRecord.from_dict(record) for record in data[self.user.username]]
                else:
                    return []
        except FileNotFoundError:
            return []

    def save_records(self):
        try:
            with open('finances.json', 'r') as f:
                data = json.load(f)
        except FileNotFoundError:
            data = {}
        
        data[self.user.username] = [record.to_dict() for record in self.records]
        
        with open('finances.json', 'w') as f:
            json.dump(data, f)

    def add_record(self):
        description = input("Enter detail: ")
        amount = float(input("Enter amount (use negative for spend): "))
        category = input("Enter category: ")
        date = datetime.now()
        record = FinanceRecord(description, amount, category, date)
        self.records.append(record)
        self.save_records()
        print("Record added successfully.")

    def delete_record(self):
        if not self.records:
            print("No records to delete.")
            return
        
        print("Select a record to delete:")
        for i, record in enumerate(self.records):
            print(f"{i+1}. {record.description} - ₹{record.amount} ({record.category})")
        
        try:
            choice = int(input("Enter the number of the record to delete: ")) - 1
            if 0 <= choice < len(self.records):
                del self.records[choice]
                self.save_records()
                print("Record deleted")
            else:
                print("wrong selection")
        except ValueError:
            print("enter a valid number.")

    def update_record(self):
        if not self.records:
            print("No records to update.")
            return
        
        print("Select a record to update:")
        for i, record in enumerate(self.records):
            print(f"{i+1}. {record.description} - ₹{record.amount} ({record.category})")
        
        try:
            choice = int(input("Enter the number of the record to update: ")) - 1
            if 0 <= choice < len(self.records):
                record = self.records[choice]
                record.description = input(f"Enter new description ({record.description}): ") or record.description
                record.amount = float(input(f"Enter new amount ({record.amount}): ") or record.amount)
                record.category = input(f"Enter new category ({record.category}): ") or record.category
                self.save_records()
                print("Record updated")
            else:
                print("Invalid selection.")
        except ValueError:
            print("Please enter a valid number.")

    def display_records(self):
        if not self.records:
            print("No records to display.")
            return
        
        for record in self.records:
            print(f"{record.date.strftime('%Y-%m-%d %H:%M:%S')} - {record.description}: ₹{record.amount} ({record.category})")

    def generate_reports(self):
        if not self.records:
            print("No records available for generating reports.")
            return

        df = pd.DataFrame([record.to_dict() for record in self.records])
        df['date'] = pd.to_datetime(df['date'])
        df['month'] = df['date'].dt.to_period('M')

        print("\nFinancial Reports")
        print("----------------")

        
        total_income = df[df['amount'] > 0]['amount'].sum()
        total_expenses = abs(df[df['amount'] < 0]['amount'].sum())
        print(f"Total Income: ₹{total_income:.2f}")
        print(f"Total Expenses: ₹{total_expenses:.2f}")

        
        print("\nSpending Distribution by Category:")
        category_spending = df[df['amount'] < 0].groupby('category')['amount'].sum().abs().sort_values(ascending=False)
        print(category_spending)

        
        print("\nMonthly Trend:")
        monthly_trends = df.groupby('month')['amount'].sum().sort_index()
        print(monthly_trends)

        
        plt.figure(figsize=(12, 6))
        
        plt.subplot(121)
        category_spending.plot(kind='pie', autopct='%1.1f%%', startangle=90)
        plt.title('Spend by Category')
        
        plt.subplot(122)
        monthly_trends.plot(kind='bar')
        plt.title('Monthly Income/Expense Trends')
        plt.xlabel('Month')
        plt.ylabel('Amount (₹)')
        
        plt.tight_layout()
        plt.savefig('financial_report.png')
        print("\nreport chart saved as 'financial_report.png'")


def main():
    print("Welcome to Personal Finance Manager")
    
    while True:
        print("\n1. Register")
        print("2. Login")
        print("3. Exit")
        choice = input("Enter your choice: ")
        
        if choice == '1':
            user = register_user()
            if user:
                manage_finances(user)
        elif choice == '2':
            user = login_user()
            if user:
                manage_finances(user)
        elif choice == '3':
            print("Thank you for using Personal Finance Manager. Goodbye!")
            break
        else:
            print("Invalid choice. Please try again.")


def manage_finances(user):
    manager = FinanceManager(user)
    
    while True:
        print(f"\nWelcome, {user.username}!")
        print("1. Add Record")
        print("2. Delete Record")
        print("3. Update Record")
        print("4. Display Records")
        print("5. Create Report")
        print("6. Logout")
        choice = input("enter your choice: ")
        
        if choice == '1':
            manager.add_record()
        elif choice == '2':
            manager.delete_record()
        elif choice == '3':
            manager.update_record()
        elif choice == '4':
            manager.display_records()
        elif choice == '5':
            manager.generate_reports()
        elif choice == '6':
            print("Logging out")
            break
        else:
            print("wrong choice. try again.")


if __name__ == "__main__":
    main()