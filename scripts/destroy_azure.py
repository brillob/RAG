"""Script to delete Azure resource group and all resources."""
import subprocess
import sys
import argparse
import time


def destroy_resources(resource_group: str, subscription_id: str = None, confirm: bool = False):
    """
    Delete an Azure resource group and all its resources.
    
    Args:
        resource_group: Name of the resource group to delete
        subscription_id: Optional subscription ID
        confirm: Skip confirmation prompt
    """
    print(f"\n⚠️  WARNING: This will delete the resource group '{resource_group}' and ALL resources in it!")
    print("   This action cannot be undone!\n")
    
    if not confirm:
        response = input(f"Are you sure you want to delete '{resource_group}'? (yes/no): ")
        if response.lower() not in ["yes", "y"]:
            print("❌ Deletion cancelled.")
            return False
    
    # Set subscription if provided
    if subscription_id:
        cmd = ["az", "account", "set", "--subscription", subscription_id]
        subprocess.run(cmd, check=False)
    
    # Check if resource group exists
    cmd = ["az", "group", "show", "--name", resource_group]
    result = subprocess.run(cmd, capture_output=True, check=False)
    if result.returncode != 0:
        print(f"❌ Resource group '{resource_group}' does not exist.")
        return False
    
    # Delete resource group
    print(f"\n🗑️  Deleting resource group '{resource_group}'...")
    cmd = ["az", "group", "delete", "--name", resource_group, "--yes", "--no-wait"]
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        print(f"✅ Deletion initiated for resource group '{resource_group}'")
        print("   Note: This may take several minutes to complete.")
        print("   You can check status with: az group show --name " + resource_group)
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to delete resource group: {e.stderr}")
        return False


def main():
    parser = argparse.ArgumentParser(description="Delete Azure resource group and all resources")
    parser.add_argument("--resource-group", required=True, help="Resource group name to delete")
    parser.add_argument("--subscription", help="Azure subscription ID")
    parser.add_argument("--yes", "-y", action="store_true", help="Skip confirmation prompt")
    
    args = parser.parse_args()
    
    # Check if Azure CLI is installed
    try:
        subprocess.run(["az", "version"], capture_output=True, check=True)
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("❌ Azure CLI is not installed or not in PATH")
        print("   Please install it from: https://aka.ms/InstallAzureCLI")
        sys.exit(1)
    
    # Check if logged in
    try:
        subprocess.run(["az", "account", "show"], capture_output=True, check=True)
    except subprocess.CalledProcessError:
        print("❌ Not logged in to Azure. Please run: az login")
        sys.exit(1)
    
    success = destroy_resources(
        resource_group=args.resource_group,
        subscription_id=args.subscription,
        confirm=args.yes
    )
    
    if not success:
        sys.exit(1)


if __name__ == "__main__":
    main()
