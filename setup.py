#!/usr/bin/env python3
"""
Setup script for Sistema de Gestão de Loja de Informática
Creates .env files automatically for Docker Compose setup
"""

import os
import shutil
import sys
from pathlib import Path

# Colors for terminal output
GREEN = '\033[92m'
YELLOW = '\033[93m'
RED = '\033[91m'
RESET = '\033[0m'

def print_success(msg):
    print(f"{GREEN}✓ {msg}{RESET}")

def print_warning(msg):
    print(f"{YELLOW}⚠ {msg}{RESET}")

def print_error(msg):
    print(f"{RED}❌ {msg}{RESET}")

def setup_env_files():
    """Create .env files from .env.example files"""

    print("\n🔧 Setting up Sistema de Gestão de Loja de Informática...\n")

    # Check if Docker is available (basic check)
    if shutil.which("docker") is None:
        print_error("Docker is not installed or not in PATH")
        print_warning("Please install Docker first: https://www.docker.com/get-started")
        return False

    print_success("Docker is installed")

    # Setup backend .env
    backend_env = Path("backend/.env")
    backend_example = Path("backend/.env.example")

    if not backend_example.exists():
        print_error(f"backend/.env.example not found in {Path.cwd()}")
        return False

    if backend_env.exists():
        print_success("backend/.env already exists")
    else:
        print_warning("Creating backend/.env from .env.example...")
        shutil.copy(backend_example, backend_env)
        print_success("Created backend/.env")

    # Setup frontend .env
    frontend_env = Path("frontend/.env")
    frontend_example = Path("frontend/.env.example")

    if not frontend_example.exists():
        print_error(f"frontend/.env.example not found in {Path.cwd()}")
        return False

    if frontend_env.exists():
        print_success("frontend/.env already exists")
    else:
        print_warning("Creating frontend/.env from .env.example...")
        shutil.copy(frontend_example, frontend_env)
        print_success("Created frontend/.env")

    return True

def print_next_steps():
    """Print instructions for running Docker Compose"""

    print(f"\n{GREEN}✓ Environment setup complete!{RESET}\n")
    print(f"{YELLOW}Next steps:{RESET}")
    print("  1. Start the application:")
    print("     docker-compose up --build")
    print("")
    print("  2. Access the services:")
    print("     - Frontend:  http://localhost:3000")
    print("     - Backend:   http://localhost:8000")
    print("     - pgAdmin:   http://localhost:5050")
    print("     - Database:  localhost:5432")
    print("")
    print(f"{YELLOW}pgAdmin credentials:{RESET}")
    print("  Email:    admin@loja.com")
    print("  Password: admin")
    print("")
    print(f"{YELLOW}Database credentials:{RESET}")
    print("  User:     postgres")
    print("  Password: postgres")
    print("  Database: loja_informatica")
    print("")

if __name__ == "__main__":
    try:
        if setup_env_files():
            print_next_steps()
            sys.exit(0)
        else:
            print_error("Setup failed")
            sys.exit(1)
    except Exception as e:
        print_error(f"An error occurred: {e}")
        sys.exit(1)
