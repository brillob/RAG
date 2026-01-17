"""Azure deployment script to create all required resources."""
import subprocess
import sys
import json
import time
import argparse
from typing import Dict, Optional


class AzureDeployment:
    """Automated Azure resource deployment."""
    
    def __init__(self, subscription_id: str, resource_group: str, location: str = "eastus"):
        """
        Initialize Azure deployment.
        
        Args:
            subscription_id: Azure subscription ID
            resource_group: Resource group name
            location: Azure region (default: eastus)
        """
        self.subscription_id = subscription_id
        self.resource_group = resource_group
        self.location = location
        self.resources = {}
    
    def run_command(self, cmd: list, check: bool = True) -> tuple[bool, str]:
        """Run an Azure CLI command."""
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                check=check
            )
            return True, result.stdout
        except subprocess.CalledProcessError as e:
            return False, e.stderr
    
    def check_resource_exists(self, resource_type: str, resource_name: str) -> bool:
        """Check if an Azure resource exists."""
        cmd = [
            "az", resource_type, "show",
            "--name", resource_name,
            "--resource-group", self.resource_group,
            "--subscription", self.subscription_id
        ]
        success, _ = self.run_command(cmd, check=False)
        return success
    
    def set_subscription(self):
        """Set the active Azure subscription."""
        cmd = ["az", "account", "set", "--subscription", self.subscription_id]
        success, output = self.run_command(cmd)
        if not success:
            print(f"Failed to set subscription: {output}")
            return False
        print(f"✓ Set subscription to {self.subscription_id}")
        return True
    
    def create_resource_group(self):
        """Create resource group if it doesn't exist."""
        if self.check_resource_exists("group", self.resource_group):
            print(f"✓ Resource group '{self.resource_group}' already exists")
            return True
        
        cmd = [
            "az", "group", "create",
            "--name", self.resource_group,
            "--location", self.location,
            "--subscription", self.subscription_id
        ]
        success, output = self.run_command(cmd)
        if success:
            print(f"✓ Created resource group '{self.resource_group}'")
            return True
        else:
            print(f"✗ Failed to create resource group: {output}")
            return False
    
    def create_search_service(self) -> Optional[Dict]:
        """Create Azure AI Search service (Free tier)."""
        service_name = f"{self.resource_group}-search"
        
        # Check if service exists
        cmd = [
            "az", "search", "service", "show",
            "--name", service_name,
            "--resource-group", self.resource_group
        ]
        success, _ = self.run_command(cmd, check=False)
        if success:
            print(f"✓ Search service '{service_name}' already exists")
            # Get existing service details
            success, output = self.run_command(cmd)
            if success:
                service_info = json.loads(output)
                # Get admin keys
                cmd = [
                    "az", "search", "admin-key", "show",
                    "--resource-group", self.resource_group,
                    "--service-name", service_name
                ]
                success, key_output = self.run_command(cmd)
                key = ""
                if success:
                    key_info = json.loads(key_output)
                    key = key_info.get("primaryKey", "")
                return {
                    "endpoint": f"https://{service_name}.search.windows.net",
                    "name": service_name,
                    "key": key
                }
            return None
        
        cmd = [
            "az", "search", "service", "create",
            "--name", service_name,
            "--resource-group", self.resource_group,
            "--sku", "free",  # Free tier
            "--location", self.location
        ]
        success, output = self.run_command(cmd)
        if success:
            print(f"✓ Created Azure AI Search service '{service_name}' (Free tier)")
            service_info = json.loads(output)
            time.sleep(10)  # Wait for service to be ready
            
            # Get admin keys
            cmd = [
                "az", "search", "admin-key", "show",
                "--resource-group", self.resource_group,
                "--service-name", service_name
            ]
            success, key_output = self.run_command(cmd)
            if success:
                key_info = json.loads(key_output)
                return {
                    "endpoint": f"https://{service_name}.search.windows.net",
                    "name": service_name,
                    "key": key_info.get("primaryKey", "")
                }
        else:
            print(f"✗ Failed to create search service: {output}")
        return None
    
    def create_openai_service(self) -> Optional[Dict]:
        """Create Azure OpenAI service (lowest tier)."""
        service_name = f"{self.resource_group}-openai"
        
        # Check if service exists
        cmd = [
            "az", "cognitiveservices", "account", "show",
            "--name", service_name,
            "--resource-group", self.resource_group
        ]
        success, _ = self.run_command(cmd, check=False)
        if success:
            print(f"✓ OpenAI service '{service_name}' already exists")
            # Get existing service details
            success, output = self.run_command(cmd)
            if success:
                service_info = json.loads(output)
                # Get keys
                cmd = [
                    "az", "cognitiveservices", "account", "keys", "list",
                    "--name", service_name,
                    "--resource-group", self.resource_group
                ]
                success, key_output = self.run_command(cmd)
                key = ""
                endpoint = ""
                if success:
                    key_info = json.loads(key_output)
                    key = key_info.get("key1", "")
                if "properties" in service_info:
                    endpoint = service_info["properties"].get("endpoint", "")
                return {
                    "name": service_name,
                    "endpoint": endpoint or f"https://{service_name}.openai.azure.com",
                    "key": key
                }
            return {"name": service_name}
        
        # Note: Azure OpenAI requires approval and may not be available in all regions
        # This is a placeholder - actual deployment may require manual approval
        cmd = [
            "az", "cognitiveservices", "account", "create",
            "--name", service_name,
            "--resource-group", self.resource_group,
            "--kind", "OpenAI",
            "--sku", "S0",  # Standard tier (lowest available)
            "--location", self.location
        ]
        success, output = self.run_command(cmd)
        if success:
            print(f"✓ Created Azure OpenAI service '{service_name}'")
            time.sleep(5)
            
            # Get keys
            cmd = [
                "az", "cognitiveservices", "account", "keys", "list",
                "--name", service_name,
                "--resource-group", self.resource_group
            ]
            success, key_output = self.run_command(cmd)
            if success:
                key_info = json.loads(key_output)
                return {
                    "name": service_name,
                    "endpoint": f"https://{service_name}.openai.azure.com",
                    "key": key_info.get("key1", "")
                }
        else:
            print(f"⚠ Azure OpenAI creation may require manual approval")
            print(f"  Please create it manually in Azure Portal if needed")
        return None
    
    def create_container_registry(self) -> Optional[Dict]:
        """Create Azure Container Registry (Basic tier - cheapest)."""
        registry_name = f"{self.resource_group}acr".replace("-", "").lower()[:50]
        
        # Check if registry exists
        cmd = [
            "az", "acr", "show",
            "--name", registry_name,
            "--resource-group", self.resource_group
        ]
        success, _ = self.run_command(cmd, check=False)
        if success:
            print(f"✓ Container Registry '{registry_name}' already exists")
            # Get credentials
            cmd = [
                "az", "acr", "credential", "show",
                "--name", registry_name
            ]
            success, cred_output = self.run_command(cmd)
            if success:
                cred_info = json.loads(cred_output)
                return {
                    "name": registry_name,
                    "username": cred_info.get("username", ""),
                    "password": cred_info.get("passwords", [{}])[0].get("value", "")
                }
            return {"name": registry_name}
        
        cmd = [
            "az", "acr", "create",
            "--name", registry_name,
            "--resource-group", self.resource_group,
            "--sku", "Basic",  # Basic tier (cheapest)
            "--admin-enabled", "true"
        ]
        success, output = self.run_command(cmd)
        if success:
            print(f"✓ Created Container Registry '{registry_name}' (Basic tier)")
            time.sleep(5)
            
            # Get credentials
            cmd = [
                "az", "acr", "credential", "show",
                "--name", registry_name
            ]
            success, cred_output = self.run_command(cmd)
            if success:
                cred_info = json.loads(cred_output)
                return {
                    "name": registry_name,
                    "username": cred_info.get("username", ""),
                    "password": cred_info.get("passwords", [{}])[0].get("value", "")
                }
        else:
            print(f"✗ Failed to create container registry: {output}")
        return None
    
    def create_app_service_plan(self) -> Optional[Dict]:
        """Create App Service Plan (Free tier)."""
        plan_name = f"{self.resource_group}-plan"
        
        # Check if plan exists
        cmd = [
            "az", "appservice", "plan", "show",
            "--name", plan_name,
            "--resource-group", self.resource_group
        ]
        success, _ = self.run_command(cmd, check=False)
        if success:
            print(f"✓ App Service Plan '{plan_name}' already exists")
            return {"name": plan_name}
        
        cmd = [
            "az", "appservice", "plan", "create",
            "--name", plan_name,
            "--resource-group", self.resource_group,
            "--sku", "F1",  # Free tier
            "--is-linux"
        ]
        success, output = self.run_command(cmd)
        if success:
            print(f"✓ Created App Service Plan '{plan_name}' (Free tier)")
            return {"name": plan_name}
        else:
            print(f"✗ Failed to create app service plan: {output}")
        return None
    
    def deploy(self) -> bool:
        """Deploy all resources."""
        print(f"\n🚀 Starting Azure deployment...")
        print(f"   Subscription: {self.subscription_id}")
        print(f"   Resource Group: {self.resource_group}")
        print(f"   Location: {self.location}\n")
        
        # Set subscription
        if not self.set_subscription():
            return False
        
        # Create resource group
        if not self.create_resource_group():
            return False
        
        # Create services
        print("\n📦 Creating Azure services...")
        self.resources["search"] = self.create_search_service()
        self.resources["openai"] = self.create_openai_service()
        self.resources["acr"] = self.create_container_registry()
        self.resources["app_plan"] = self.create_app_service_plan()
        
        # Print summary
        print("\n" + "="*60)
        print("📋 Deployment Summary")
        print("="*60)
        
        if self.resources["search"]:
            print(f"\n✓ Azure AI Search:")
            print(f"   Endpoint: {self.resources['search'].get('endpoint', 'N/A')}")
            print(f"   Name: {self.resources['search'].get('name', 'N/A')}")
        
        if self.resources["openai"]:
            print(f"\n✓ Azure OpenAI:")
            print(f"   Name: {self.resources['openai'].get('name', 'N/A')}")
            print(f"   ⚠ Note: May require manual model deployment")
        
        if self.resources["acr"]:
            print(f"\n✓ Container Registry:")
            print(f"   Name: {self.resources['acr'].get('name', 'N/A')}")
        
        print("\n" + "="*60)
        print("✅ Deployment completed!")
        print("\nNext steps:")
        print("1. Configure your .env file with the resource details above")
        print("2. Create and index your knowledge base in Azure AI Search")
        print("3. Deploy your model to Azure OpenAI")
        print("4. Build and push your Docker image to ACR")
        print("="*60)
        
        return True


def main():
    parser = argparse.ArgumentParser(description="Deploy RAG system to Azure")
    parser.add_argument("--subscription", required=True, help="Azure subscription ID")
    parser.add_argument("--resource-group", required=True, help="Resource group name")
    parser.add_argument("--location", default="eastus", help="Azure region (default: eastus)")
    
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
    
    deployment = AzureDeployment(
        subscription_id=args.subscription,
        resource_group=args.resource_group,
        location=args.location
    )
    
    if not deployment.deploy():
        print("\n❌ Deployment failed!")
        sys.exit(1)


if __name__ == "__main__":
    main()
