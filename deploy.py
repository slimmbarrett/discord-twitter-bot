#!/usr/bin/env python3
import os
import sys
import platform
import subprocess
import shutil
import argparse
from pathlib import Path

def print_header(message):
    """Print a formatted header message"""
    print("\n" + "=" * 50)
    print(f" {message}")
    print("=" * 50)

def print_step(message):
    """Print a step message"""
    print(f"\n>> {message}")

def is_command_available(command):
    """Check if a command is available in PATH"""
    return shutil.which(command) is not None

def setup_venv():
    """Setup virtual environment and install dependencies"""
    print_step("Setting up virtual environment...")
    
    venv_path = Path(".venv")
    if venv_path.exists():
        print("Virtual environment already exists")
    else:
        subprocess.run([sys.executable, "-m", "venv", ".venv"], check=True)
    
    # Activate virtual environment
    if platform.system() == "Windows":
        pip_path = venv_path / "Scripts" / "pip"
        python_path = venv_path / "Scripts" / "python"
    else:
        pip_path = venv_path / "bin" / "pip"
        python_path = venv_path / "bin" / "python"
    
    print_step("Installing dependencies...")
    subprocess.run([str(pip_path), "install", "--upgrade", "pip"], check=True)
    subprocess.run([str(pip_path), "install", "-r", "requirements.txt"], check=True)
    
    return python_path

def setup_env_file():
    """Setup .env file"""
    print_step("Setting up .env file...")
    
    if os.path.exists(".env"):
        print(".env file already exists")
        return
    
    if os.path.exists(".env.example"):
        shutil.copy(".env.example", ".env")
        print("Created .env file from .env.example")
        print("Please edit .env file with your credentials")
    else:
        print("ERROR: .env.example file not found")
        sys.exit(1)

def create_db_tables(python_path):
    """Create database tables"""
    print_step("Creating database tables...")
    
    subprocess.run([str(python_path), "create_tables.py"], check=True)

def setup_systemd():
    """Setup systemd service for Linux"""
    print_step("Setting up systemd service...")
    
    if not is_command_available("systemctl"):
        print("Systemd not available on this system")
        return False
    
    print("You need root privileges to install systemd service.")
    print("Run the following command to install the service:")
    print("  sudo ./start_bot_service.sh")
    return True

def setup_docker():
    """Setup Docker deployment"""
    print_step("Setting up Docker deployment...")
    
    if not is_command_available("docker"):
        print("Docker not available on this system")
        return False
    
    print("Building Docker image...")
    subprocess.run(["docker", "build", "-t", "discord-twitter-bot", "."], check=True)
    
    print("\nDocker setup complete!")
    print("To run the bot in Docker, use:")
    print("  docker run -d --name discord-bot discord-twitter-bot")
    return True

def setup_screen():
    """Setup screen for unix systems"""
    print_step("Setting up screen deployment...")
    
    if not is_command_available("screen"):
        print("Screen not available on this system")
        return False
    
    print("To run the bot using screen, use:")
    print("  screen -S discord-bot")
    print("  ./fix_init.sh")
    print("  (Press Ctrl+A then D to detach)")
    return True

def setup_windows_service():
    """Setup Windows service using NSSM"""
    print_step("Setting up Windows service...")
    
    if platform.system() != "Windows":
        return False
    
    if not is_command_available("nssm"):
        print("NSSM not available. Please install it: https://nssm.cc/")
        return False
    
    script_path = os.path.abspath("fix_zsh_error.py")
    python_path = os.path.abspath(sys.executable)
    
    print("Run the following command as Administrator:")
    print(f'  nssm install DiscordTwitterBot "{python_path}" "{script_path}"')
    print("Then start the service:")
    print("  nssm start DiscordTwitterBot")
    return True

def setup_github_actions():
    """Setup GitHub Actions for CI/CD"""
    print_step("Setting up GitHub Actions for CI/CD...")
    
    workflows_dir = Path(".github/workflows")
    workflows_dir.mkdir(parents=True, exist_ok=True)
    
    workflow_file = workflows_dir / "deploy.yml"
    
    workflow_content = """name: Deploy Discord Bot

on:
  push:
    branches: [ main ]
  workflow_dispatch:

jobs:
  deploy:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v2
    
    - name: Set up Python
      uses: actions/setup-python@v2
      with:
        python-version: '3.10'
    
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        if [ -f requirements.txt ]; then pip install -r requirements.txt; fi
    
    - name: Deploy to server
      uses: appleboy/ssh-action@master
      with:
        host: ${{ secrets.HOST }}
        username: ${{ secrets.USERNAME }}
        key: ${{ secrets.SSH_KEY }}
        script: |
          cd /path/to/discord-twitter-bot
          git pull
          source .venv/bin/activate
          pip install -r requirements.txt
          sudo systemctl restart discord-twitter-bot
"""
    
    with open(workflow_file, "w") as f:
        f.write(workflow_content)
    
    print(f"Created GitHub Actions workflow file: {workflow_file}")
    print("For GitHub Actions to work, you need to set up secrets in your GitHub repository:")
    print("  HOST: Your server hostname or IP")
    print("  USERNAME: SSH username")
    print("  SSH_KEY: Private SSH key for authentication")
    return True

def main():
    """Main function to run the setup process"""
    parser = argparse.ArgumentParser(description="Deploy Discord Twitter bot to various platforms")
    parser.add_argument("--systemd", action="store_true", help="Deploy as systemd service (Linux)")
    parser.add_argument("--docker", action="store_true", help="Deploy using Docker")
    parser.add_argument("--screen", action="store_true", help="Deploy using screen (Unix)")
    parser.add_argument("--windows", action="store_true", help="Deploy as Windows service")
    parser.add_argument("--github", action="store_true", help="Setup GitHub Actions for CI/CD")
    parser.add_argument("--all", action="store_true", help="Setup all available deployment methods")
    parser.add_argument("--skip-venv", action="store_true", help="Skip virtual environment setup")
    
    args = parser.parse_args()
    
    print_header("Discord Twitter Bot Deployment")
    
    # Setup virtual environment unless skipped
    python_path = None
    if not args.skip_venv:
        python_path = setup_venv()
    
    # Setup .env file
    setup_env_file()
    
    # Create database tables (requires env file to be set up)
    if python_path:
        try:
            create_db_tables(python_path)
        except subprocess.CalledProcessError:
            print("Warning: Failed to create database tables. Please check your .env file and Supabase credentials.")
    
    # Determine which deployment methods to use
    if args.all:
        setup_systemd()
        setup_docker()
        setup_screen()
        setup_windows_service()
        setup_github_actions()
    else:
        methods_selected = False
        
        if args.systemd:
            methods_selected = setup_systemd() or methods_selected
        
        if args.docker:
            methods_selected = setup_docker() or methods_selected
        
        if args.screen:
            methods_selected = setup_screen() or methods_selected
        
        if args.windows:
            methods_selected = setup_windows_service() or methods_selected
        
        if args.github:
            methods_selected = setup_github_actions() or methods_selected
        
        if not methods_selected:
            print_step("No deployment method selected or all selected methods failed")
            print("Available methods:")
            print("  --systemd  : Deploy as systemd service (Linux)")
            print("  --docker   : Deploy using Docker")
            print("  --screen   : Deploy using screen (Unix)")
            print("  --windows  : Deploy as Windows service")
            print("  --github   : Setup GitHub Actions for CI/CD")
            print("  --all      : Setup all available deployment methods")
    
    print_header("Deployment setup complete!")
    print("Please make sure to:")
    print("1. Edit the .env file with your credentials")
    print("2. Invite your bot to your Discord server")
    print("3. Start the bot using one of the configured deployment methods")

if __name__ == "__main__":
    main() 