import json

# Function to print all accounts
def print_all_accounts(file_path):
    with open(file_path, 'r') as f:
        data = json.load(f)
    
    print("Existing Accounts:")
    for account in data['accounts']:
        print(f"{account['id']}, {account['name']} (created: {account['date']})")

# Function to add a new account
def add_account(file_path):
    with open(file_path, 'r') as f:
        data = json.load(f)
    
    # Prompt for account details
    print("\nAdd a New Account:")
    account_id = str(len(data['accounts']) + 1)  # New account id is the next available number
    
    date = input("Enter date: ")
    name = input("Enter name: ")
    access_key_id = input("Enter key id: ")
    access_key_secret = input("Enter key secret: ")
    region_id = "ap-southeast-5"  # Default region ID
    
    new_account = {
        "id": account_id,
        "date": date,
        "name": name,
        "access_key_id": access_key_id,
        "access_key_secret": access_key_secret,
        "region_id": region_id
    }
    
    # Add new account to the data
    data['accounts'].append(new_account)
    
    # Save updated data to file
    with open(file_path, 'w') as f:
        json.dump(data, f, indent=4)
    
    print(f"\nNew account added: ID {account_id}, Name {name}")

# Function to remove an account by ID
def remove_account(file_path, account_id):
    with open(file_path, 'r') as f:
        data = json.load(f)
    
    # Filter out the account with the given ID
    data['accounts'] = [account for account in data['accounts'] if account['id'] != account_id]
    
    # Save updated data to file
    with open(file_path, 'w') as f:
        json.dump(data, f, indent=4)
    
    print(f"Account with ID {account_id} removed.")

# Main function to manage accounts
def main():
    file_path = 'access.json'

    # Display all accounts
    print_all_accounts(file_path)

    # Prompt to add a new account
    add_new = input("\nDo you want to add a new account? (y/n): ").strip().lower()
    if add_new == 'y':
        add_account(file_path)
    
    # Optionally, you could add a function to remove an account as well
    remove_account_input = input("\nDo you want to remove an account? (y/n): ").strip().lower()
    if remove_account_input == 'y':
        account_id_to_remove = input("Enter the ID of the account to remove: ").strip()
        remove_account(file_path, account_id_to_remove)

    # Display the updated list of accounts
    print("\nUpdated Accounts:")
    print_all_accounts(file_path)

if __name__ == "__main__":
    main()
