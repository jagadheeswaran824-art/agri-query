#!/usr/bin/env python3
"""
KrishiSahay API Key Setup Script
Interactive script to configure IBM Watsonx API credentials
"""

import os
import sys

def print_header():
    print("""
╔═══════════════════════════════════════════════════════════════════════════════╗
║                                                                               ║
║   🔑 KrishiSahay API Key Configuration                                       ║
║   IBM Watsonx Granite LLM Setup                                              ║
║                                                                               ║
╚═══════════════════════════════════════════════════════════════════════════════╝
    """)

def print_instructions():
    print("""
📚 Before you begin, you need:

1. IBM Cloud Account
   → Sign up at: https://cloud.ibm.com/registration

2. IBM Watsonx Access
   → Request access at: https://www.ibm.com/watsonx

3. API Key
   → Get from: https://cloud.ibm.com/iam/apikeys
   → Click "Create an IBM Cloud API key"
   → Copy and save the key

4. Project ID
   → Go to: https://dataplatform.cloud.ibm.com/wx/home
   → Navigate to your project
   → Find Project ID in Manage tab

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    """)

def get_input(prompt, default=""):
    """Get user input with optional default value"""
    if default:
        user_input = input(f"{prompt} [{default}]: ").strip()
        return user_input if user_input else default
    else:
        while True:
            user_input = input(f"{prompt}: ").strip()
            if user_input:
                return user_input
            print("❌ This field is required. Please enter a value.")

def validate_api_key(api_key):
    """Basic validation for API key format"""
    if len(api_key) < 20:
        return False, "API key seems too short"
    return True, "Valid"

def validate_project_id(project_id):
    """Basic validation for project ID format"""
    if len(project_id) < 10:
        return False, "Project ID seems too short"
    return True, "Valid"

def update_env_file(api_key, project_id, region):
    """Update .env file with API credentials"""
    env_content = f"""# IBM Watsonx Configuration
# Get your API key from: https://cloud.ibm.com/iam/apikeys
# Get your Project ID from: https://dataplatform.cloud.ibm.com/wx/home
WATSONX_API_KEY={api_key}
WATSONX_PROJECT_ID={project_id}
WATSONX_REGION={region}

# Model Configuration
MODEL_ID=ibm/granite-3-8b-instruct
EMBEDDING_MODEL=all-MiniLM-L6-v2

# Application Settings
TOP_K_RESULTS=5
MAX_TOKENS=1000
TEMPERATURE=0.7

# Server Configuration
PORT=5000
DEBUG=False

# Flask Configuration
SECRET_KEY=krishisahay-secret-key-2024
"""
    
    try:
        with open('.env', 'w') as f:
            f.write(env_content)
        return True
    except Exception as e:
        print(f"❌ Error writing .env file: {e}")
        return False

def set_environment_variables(api_key, project_id, region):
    """Set environment variables for current session"""
    os.environ['WATSONX_API_KEY'] = api_key
    os.environ['WATSONX_PROJECT_ID'] = project_id
    os.environ['WATSONX_REGION'] = region
    print("✅ Environment variables set for current session")

def test_configuration():
    """Test the Watsonx configuration"""
    print("\n🧪 Testing Watsonx configuration...")
    
    try:
        from watsonx_integration import WatsonxGraniteAI
        
        watsonx = WatsonxGraniteAI()
        
        if watsonx.is_available:
            print("✅ Watsonx configuration is valid!")
            
            # Try to authenticate
            token = watsonx.authenticate()
            if token:
                print("✅ Authentication successful!")
                print(f"   Model: {watsonx.model_id}")
                print(f"   Region: {watsonx.region}")
                return True
            else:
                print("❌ Authentication failed. Please check your API key.")
                return False
        else:
            print("❌ Watsonx is not available. Please check your credentials.")
            return False
            
    except Exception as e:
        print(f"❌ Error testing configuration: {e}")
        return False

def main():
    print_header()
    
    print("This script will help you configure IBM Watsonx API credentials.\n")
    
    # Ask if user wants to see instructions
    show_instructions = input("📖 Do you want to see setup instructions? (y/n) [y]: ").strip().lower()
    if show_instructions != 'n':
        print_instructions()
    
    print("\n🔧 Let's configure your API credentials:\n")
    
    # Get API Key
    print("1️⃣  IBM Cloud API Key")
    api_key = get_input("   Enter your IBM Cloud API key")
    
    # Validate API key
    is_valid, message = validate_api_key(api_key)
    if not is_valid:
        print(f"   ⚠️  Warning: {message}")
        confirm = input("   Continue anyway? (y/n) [n]: ").strip().lower()
        if confirm != 'y':
            print("❌ Setup cancelled.")
            return
    else:
        print(f"   ✅ {message}")
    
    # Get Project ID
    print("\n2️⃣  Watsonx Project ID")
    project_id = get_input("   Enter your Watsonx Project ID")
    
    # Validate project ID
    is_valid, message = validate_project_id(project_id)
    if not is_valid:
        print(f"   ⚠️  Warning: {message}")
        confirm = input("   Continue anyway? (y/n) [n]: ").strip().lower()
        if confirm != 'y':
            print("❌ Setup cancelled.")
            return
    else:
        print(f"   ✅ {message}")
    
    # Get Region
    print("\n3️⃣  Watsonx Region")
    print("   Available regions:")
    print("   • us-south (Dallas) - Default")
    print("   • eu-gb (London)")
    print("   • eu-de (Frankfurt)")
    print("   • jp-tok (Tokyo)")
    region = get_input("   Enter region", "us-south")
    print(f"   ✅ Region set to: {region}")
    
    # Confirm configuration
    print("\n" + "="*80)
    print("📋 Configuration Summary:")
    print("="*80)
    print(f"API Key: {api_key[:10]}...{api_key[-10:]}")
    print(f"Project ID: {project_id}")
    print(f"Region: {region}")
    print("="*80)
    
    confirm = input("\n✅ Save this configuration? (y/n) [y]: ").strip().lower()
    if confirm == 'n':
        print("❌ Setup cancelled.")
        return
    
    # Update .env file
    print("\n💾 Saving configuration to .env file...")
    if update_env_file(api_key, project_id, region):
        print("✅ Configuration saved to .env file")
    else:
        print("❌ Failed to save configuration")
        return
    
    # Set environment variables
    print("\n🔧 Setting environment variables...")
    set_environment_variables(api_key, project_id, region)
    
    # Test configuration
    test_config = input("\n🧪 Do you want to test the configuration now? (y/n) [y]: ").strip().lower()
    if test_config != 'n':
        if test_configuration():
            print("\n" + "="*80)
            print("🎉 SUCCESS! IBM Watsonx is configured and ready to use!")
            print("="*80)
            print("\n📝 Next steps:")
            print("   1. Restart the Flask backend server")
            print("   2. Open http://localhost:5000")
            print("   3. Start chatting with AI-powered responses!")
            print("\n💡 To restart the server:")
            print("   python flask_backend.py")
        else:
            print("\n⚠️  Configuration saved but authentication failed.")
            print("   Please verify your credentials and try again.")
    else:
        print("\n✅ Configuration saved!")
        print("   Restart the server to apply changes:")
        print("   python flask_backend.py")
    
    print("\n" + "="*80)
    print("📚 For more information, see: WATSONX_SETUP_GUIDE.md")
    print("="*80)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n❌ Setup cancelled by user.")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ An error occurred: {e}")
        sys.exit(1)