import time
import json
import uuid
import hashlib
import hmac
import base64
import requests
from urllib.parse import urlencode, quote_plus
from aliyunsdkcore.client import AcsClient
from aliyunsdkcore.request import CommonRequest
from colorama import Fore as ff, Style


# Region mapping for display purposes
reg_id = {
    'ap-southeast-1': 'SG',
    'ap-southeast-3': 'MY',
    'ap-southeast-5': 'ID'
}

# ------------------------------------------
# Helper functions
# ------------------------------------------

def percent_encode(value):
    return quote_plus(value, safe='')

def compute_signature(params, secret):
    sorted_params = sorted(params.items(), key=lambda x: x[0])
    query_string = urlencode(sorted_params)
    string_to_sign = f"GET&%2F&{percent_encode(query_string)}"
    hashed = hmac.new(
        (secret + "&").encode('utf-8'),
        string_to_sign.encode('utf-8'),
        hashlib.sha1
    )
    return base64.b64encode(hashed.digest()).decode('utf-8')

def make_request(action, params, access_key_id, access_key_secret):
    base_url = "https://ecs.aliyuncs.com/"
    default_params = {
        "Format": "JSON",
        "Version": "2014-05-26",
        "AccessKeyId": access_key_id,
        "SignatureMethod": "HMAC-SHA1",
        "Timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "SignatureVersion": "1.0",
        "SignatureNonce": str(uuid.uuid4()),
        "Action": action,
    }
    default_params.update(params)
    signature = compute_signature(default_params, access_key_secret)
    default_params["Signature"] = signature
    response = requests.get(base_url, params=default_params)
    return response.json()

def list_images(access_key_id, access_key_secret, region_id):
    response = make_request(
        "DescribeImages",
        {"RegionId": region_id, "PageSize": 100},
        access_key_id,
        access_key_secret,
    )
    return response.get("Images", {}).get("Image", [])

def load_accounts(file_path):
    with open(file_path, "r") as file:
        data = json.load(file)
    return data.get("accounts", [])

def select_account(accounts):
    print("\nAvailable Accounts:")
    for i, account in enumerate(accounts, 1):
        reg = f"{account['region_id']}"
        rg = reg_id.get(reg)
        print(f"{i}. {account['name']} (Region: {rg})")
    selected = input("Enter account number: ")
    if selected.isdigit() and 1 <= int(selected) <= len(accounts):
        return accounts[int(selected) - 1]
    print("Invalid selection.")
    return None

def list_instances(client, region_id):
    try:
        request = CommonRequest()
        request.set_accept_format('json')
        request.set_domain('ecs.aliyuncs.com')
        request.set_version('2014-05-26')
        request.set_action_name('DescribeInstances')
        request.add_query_param('RegionId', region_id)
        response = client.do_action(request)
        instances = json.loads(response.decode('utf-8')).get('Instances', {}).get('Instance', [])
        return instances
    except Exception as e:
        print(f"Error fetching instances: {str(e)}")
        return []

def rebuild_instance(client, region_id, instance_id, image_id):
    try:
        request = CommonRequest()
        request.set_accept_format('json')
        request.set_domain('ecs.aliyuncs.com')
        request.set_version('2014-05-26')
        request.set_action_name('ReplaceSystemDisk')
        request.add_query_param('RegionId', region_id)
        request.add_query_param('InstanceId', instance_id)
        request.add_query_param('ImageId', image_id)
        request.add_query_param('Password', 'new_password_here')  # Add desired password
        response = client.do_action(request)
        print(f"Rebuild instance with Image ID {image_id}: {response.decode('utf-8')}")
    except Exception as e:
        print(f"Error rebuilding instance: {str(e)}")

def reset_password_and_enable_auth(client, instance_id, region_id, new_password):
    try:
        request = CommonRequest()
        request.set_accept_format('json')
        request.set_domain('ecs.aliyuncs.com')
        request.set_version('2014-05-26')
        request.set_action_name('ModifyInstanceAttribute')
        request.add_query_param('RegionId', region_id)
        request.add_query_param('InstanceId', instance_id)
        request.add_query_param('Password', new_password)
        request.add_query_param('PasswordAuthentication', 'true')
        response = client.do_action(request)
        print(f"Password reset and authentication enabled: {response.decode('utf-8')}")
    except Exception as e:
        print(f"Error modifying instance attribute: {str(e)}")

def reboot_instance(client, instance_id, region_id):
    try:
        request = CommonRequest()
        request.set_accept_format('json')
        request.set_domain('ecs.aliyuncs.com')
        request.set_version('2014-05-26')
        request.set_action_name('RebootInstance')
        request.add_query_param('RegionId', region_id)
        request.add_query_param('InstanceId', instance_id)
        response = client.do_action(request)
        print(f"Instance {instance_id} rebooted successfully: {response.decode('utf-8')}")
    except Exception as e:
        print(f"Error rebooting instance: {str(e)}")


# ------------------------------------------
# New function for printing all accounts
# ------------------------------------------

def print_all_accounts(file_path):
    with open(file_path, 'r') as f:
        data = json.load(f)

    print("Existing Accounts:")
    for account in data['accounts']:
        print(f"{account['id']}, {account['name']} (created: {account['date']})")


# ------------------------------------------
# Menu-driven main function
# ------------------------------------------

# ------------------------------------------
# Menu-driven main function
# ------------------------------------------

def main():
    file_path = 'access.json'

    while True:
        print("\n--- Main Menu ---")
        print("1. Manage Accounts")
        print("2. List Images")
        print("3. Manage Instances")
        print("4. Exit")
        
        choice = input("Enter your choice: ")

        if choice == '1':  # Manage Accounts
            print("\n--- Account Management ---")
            print("1. Add New Account")
            print("2. Remove Account")
            print("3. Show All Accounts")
            print("4. Go Back")
            
            account_choice = input("Enter your choice: ")

            if account_choice == '1':  # Add Account
                add_account(file_path)
            elif account_choice == '2':  # Remove Account
                account_id_to_remove = input("Enter the ID of the account to remove: ").strip()
                remove_account(file_path, account_id_to_remove)
            elif account_choice == '3':  # Show All Accounts
                print_all_accounts(file_path)
            elif account_choice == '4':  # Go Back
                continue
            else:
                print("Invalid choice. Try again.")

        elif choice == '2':  # List Images
            accounts = load_accounts(file_path)
            selected_account = select_account(accounts)
            if not selected_account:
                print("No account selected.")
                continue

            print(f"\nListing images for account: {selected_account['name']} (Region: {selected_account['region_id']})")
            images = list_images(
                selected_account["access_key_id"],
                selected_account["access_key_secret"],
                selected_account["region_id"]
            )

            if images:
                images_sorted = sorted(images, key=lambda x: x.get("ImageName", "").lower())
                print(f"\nAvailable Images in Region {selected_account['region_id']} (Sorted by Name):")
                for image in images_sorted:
                    print(f"OS Name: {ff.RED}{image.get('OSName', 'N/A')}{Style.RESET_ALL}\nImage ID: {ff.GREEN}{image['ImageId']}{Style.RESET_ALL}")
            else:
                print(f"No images available in region: {selected_account['region_id']}")

        elif choice == '3':  # Manage Instances
            accounts = load_accounts(file_path)
            selected_account = select_account(accounts)
            if not selected_account:
                print("No account selected.")
                continue

            client = AcsClient(selected_account['access_key_id'], selected_account['access_key_secret'], selected_account['region_id'])
            instances = list_instances(client, selected_account['region_id'])
            if not instances:
                print("No instances found.")
                continue

            print("\nAvailable Instances:")
            for i, instance in enumerate(instances, 1):
                print(f"{i}. {instance['InstanceName']} (ID: {instance['InstanceId']}, Status: {instance['Status']})")

            selected_instance_index = int(input("Enter the instance number to select: "))
            selected_instance = instances[selected_instance_index - 1]
            instance_id = selected_instance['InstanceId']

            print("\nInstance Management:")
            print("1. Rebuild Instance")
            print("2. Reset Password & Reboot")
            print("3. Reboot Instance")  # New option for reboot
            print("4. Go Back")

            instance_choice = input("Enter your choice: ")

            if instance_choice == '1':  # Rebuild Instance
                image_id = input("Enter Image ID to rebuild with: ")
                rebuild_instance(client, selected_account['region_id'], instance_id, image_id)
            elif instance_choice == '2':  # Reset Password & Reboot
                new_password = "new_password_here"
                reset_password_and_enable_auth(client, instance_id, selected_account['region_id'], new_password)
                reboot_instance(client, instance_id, selected_account['region_id'])
            elif instance_choice == '3':  # Reboot Instance (new option)
                reboot_instance(client, instance_id, selected_account['region_id'])
            elif instance_choice == '4':  # Go Back
                continue
            else:
                print("Invalid choice. Try again.")

        elif choice == '4':  # Exit
            print("Exiting program.")
            break

        else:
            print("Invalid choice. Try again.")

if __name__ == "__main__":
    main()
