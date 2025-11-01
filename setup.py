"""
Setup script for Event Management System
This script helps set up the Django project for the first time.
"""

import os
import sys
import subprocess

def run_command(command):
    """Run a shell command and return success status."""
    try:
        subprocess.run(command, shell=True, check=True)
        return True
    except subprocess.CalledProcessError:
        return False

def main():
    print("Event Management System - Setup Script")
    print("=" * 50)
    
    # Check if virtual environment exists
    if not os.path.exists('venv'):
        print("\n1. Creating virtual environment...")
        if not run_command(f"{sys.executable} -m venv venv"):
            print("ERROR: Failed to create virtual environment")
            return
        print("✓ Virtual environment created")
    else:
        print("✓ Virtual environment already exists")
    
    # Determine activate script based on OS
    if sys.platform == 'win32':
        activate_script = 'venv\\Scripts\\activate'
        pip_cmd = 'venv\\Scripts\\pip'
    else:
        activate_script = 'source venv/bin/activate'
        pip_cmd = 'venv/bin/pip'
    
    print("\n2. Installing dependencies...")
    if not run_command(f"{pip_cmd} install -r requirements.txt"):
        print("ERROR: Failed to install dependencies")
        print("Please run manually: pip install -r requirements.txt")
        return
    print("✓ Dependencies installed")
    
    print("\n3. Running migrations...")
    python_cmd = 'venv\\Scripts\\python' if sys.platform == 'win32' else 'venv/bin/python'
    if not run_command(f"{python_cmd} manage.py migrate"):
        print("ERROR: Failed to run migrations")
        return
    print("✓ Migrations completed")
    
    print("\n4. Creating .env file...")
    if not os.path.exists('.env'):
        env_content = """SECRET_KEY=django-insecure-change-this-in-production
DEBUG=True
CELERY_BROKER_URL=redis://localhost:6379/0
CELERY_RESULT_BACKEND=redis://localhost:6379/0
"""
        with open('.env', 'w') as f:
            f.write(env_content)
        print("✓ .env file created (please configure email settings)")
    else:
        print("✓ .env file already exists")
    
    print("\n" + "=" * 50)
    print("Setup complete!")
    print("\nNext steps:")
    print("1. Activate virtual environment:")
    if sys.platform == 'win32':
        print("   venv\\Scripts\\activate")
    else:
        print("   source venv/bin/activate")
    print("2. Start Redis (required for Celery):")
    print("   - Windows: docker run -d -p 6379:6379 redis")
    print("   - macOS: brew services start redis")
    print("   - Linux: sudo systemctl start redis")
    print("3. Start Django server:")
    print("   python manage.py runserver")
    print("4. Start Celery worker (in another terminal):")
    print("   celery -A event_management worker --loglevel=info")
    print("\nFor more information, see README.md")

if __name__ == '__main__':
    main()

