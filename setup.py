#!/usr/bin/env python3
import os
import sys
import subprocess
import shutil

def check_python_version():
    """Check if Python version is 3.9 or higher"""
    if sys.version_info < (3, 9):
        print("Error: Python 3.9 or higher is required.")
        sys.exit(1)
    print("✅ Python version check passed")

def check_pip():
    """Check if pip is installed"""
    try:
        subprocess.run(["pip", "--version"], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        print("✅ pip is installed")
        return True
    except (subprocess.SubprocessError, FileNotFoundError):
        print("❌ pip is not installed")
        return False

def install_dependencies():
    """Install dependencies from requirements.txt"""
    print("Installing dependencies...")
    try:
        subprocess.run(["pip", "install", "-r", "requirements.txt"], check=True)
        print("✅ Dependencies installed successfully")
        return True
    except subprocess.SubprocessError:
        print("❌ Failed to install dependencies")
        return False

def create_env_file():
    """Create .env file from .env.example if it doesn't exist"""
    if not os.path.exists(".env"):
        if os.path.exists(".env.example"):
            print("Creating .env file from .env.example...")
            shutil.copy(".env.example", ".env")
            print("✅ .env file created")
            print("⚠️ Please edit the .env file and add your API keys and tokens")
        else:
            print("❌ .env.example file not found")
            return False
    else:
        print("✅ .env file already exists")
    return True

def check_discord_token():
    """Check if Discord token is set in .env file"""
    if os.path.exists(".env"):
        with open(".env", "r") as f:
            for line in f:
                if line.startswith("DISCORD_TOKEN=") and line.strip() != "DISCORD_TOKEN=your_discord_bot_token":
                    print("✅ Discord token is set")
                    return True
        print("❌ Discord token is not set in .env file")
        return False
    return False

def main():
    """Main setup function"""
    print("TweetSync Bot Setup")
    print("=================")
    
    # Check Python version
    check_python_version()
    
    # Check pip
    if not check_pip():
        print("Please install pip and try again.")
        sys.exit(1)
    
    # Install dependencies
    if not install_dependencies():
        print("Please install the dependencies manually and try again.")
        sys.exit(1)
    
    # Create .env file
    if not create_env_file():
        print("Please create a .env file manually based on the .env.example file.")
    
    # Check Discord token
    if not check_discord_token():
        print("Please set your Discord token in the .env file.")
    
    print("\nSetup completed!")
    print("To start the bot, run: python bot.py")

if __name__ == "__main__":
    main() 