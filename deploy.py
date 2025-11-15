#!/usr/bin/env python3
"""
Automated deployment script for GSR Analytics to test server
Usage: python deploy.py
"""

import os
import sys
import subprocess
import tarfile
from pathlib import Path

# Server configuration
SERVER = "192.168.99.124"
USER = "silentoutlaw"
PASSWORD = "hyRule-penneewarp"
REMOTE_DIR = "/home/silentoutlaw/gsr-analytics"

def run_command(cmd, shell=True):
    """Run a command and return output"""
    try:
        result = subprocess.run(cmd, shell=shell, capture_output=True, text=True, timeout=30)
        return result.returncode == 0, result.stdout, result.stderr
    except Exception as e:
        return False, "", str(e)

def create_deployment_package():
    """Create tarball of project"""
    print("[*] Creating deployment package...")

    exclude_patterns = [
        'node_modules', '.next', '__pycache__', '*.pyc', '.git',
        'gsr-analytics.tar.gz', 'gsr-deploy.tar.gz', '*.tar.gz'
    ]

    # Create tarball
    with tarfile.open('gsr-deploy.tar.gz', 'w:gz') as tar:
        for item in ['backend', 'frontend', 'docker-compose.yml', 'docs', 'prompts', 'memory', 'infra', 'CLAUDE.md', 'README.md', 'QUICKSTART.md']:
            if os.path.exists(item):
                print(f"  Adding {item}...")
                tar.add(item, arcname=item)

    print("[+] Package created: gsr-deploy.tar.gz\n")
    return True

def deploy_via_ssh():
    """Deploy to server using SSH"""
    print(f"[*] Deploying to {SERVER}...")

    # Check if we can use scp/ssh directly
    # On Windows, we'll use paramiko for better password handling
    try:
        import paramiko
        use_paramiko = True
    except ImportError:
        print("⚠️  paramiko not found. Install with: pip install paramiko")
        use_paramiko = False

    if use_paramiko:
        return deploy_with_paramiko()
    else:
        return deploy_with_manual_steps()

def deploy_with_paramiko():
    """Deploy using paramiko library"""
    import paramiko
    from scp import SCPClient

    print("[*] Connecting via SSH...")

    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    try:
        ssh.connect(SERVER, username=USER, password=PASSWORD, timeout=10)
        print("[+] Connected!\n")

        # Upload file
        print("[*] Uploading deployment package...")
        with SCPClient(ssh.get_transport()) as scp:
            scp.put('gsr-deploy.tar.gz', '/home/silentoutlaw/gsr-deploy.tar.gz')
        print("[+] Upload complete!\n")

        # Execute deployment commands
        commands = [
            f"mkdir -p {REMOTE_DIR}",
            f"tar -xzf ~/gsr-deploy.tar.gz -C {REMOTE_DIR}",
            f"cd {REMOTE_DIR} && ls -la",
            f"cd {REMOTE_DIR} && docker-compose --version",
        ]

        for cmd in commands:
            print(f"[*] Running: {cmd}")
            stdin, stdout, stderr = ssh.exec_command(cmd)
            output = stdout.read().decode()
            error = stderr.read().decode()
            if output:
                print(f"   {output}")
            if error and 'warning' not in error.lower():
                print(f"   Error: {error}")

        print("\n[+] Deployment complete!")
        print(f"\n[*] Next steps:")
        print(f"1. SSH to server: ssh {USER}@{SERVER}")
        print(f"2. Configure: cd {REMOTE_DIR} && cp backend/.env.example backend/.env")
        print(f"3. Start: docker-compose up -d")
        print(f"4. Initialize DB: docker-compose exec backend alembic upgrade head")
        print(f"5. Test: curl http://{SERVER}:8000/health")

        ssh.close()
        return True

    except Exception as e:
        print(f"[-] Error: {e}")
        print("\nTrying manual deployment method...")
        return deploy_with_manual_steps()

def deploy_with_manual_steps():
    """Provide manual deployment steps"""
    print("\n[*] Manual Deployment Steps:")
    print(f"\n1. Copy package to server:")
    print(f"   scp gsr-deploy.tar.gz {USER}@{SERVER}:~/")
    print(f"\n2. SSH to server:")
    print(f"   ssh {USER}@{SERVER}")
    print(f"   Password: {PASSWORD}")
    print(f"\n3. Extract and setup:")
    print(f"   mkdir -p {REMOTE_DIR}")
    print(f"   tar -xzf ~/gsr-deploy.tar.gz -C {REMOTE_DIR}")
    print(f"   cd {REMOTE_DIR}")
    print(f"\n4. Configure environment:")
    print(f"   cp backend/.env.example backend/.env")
    print(f"   nano backend/.env  # Add API keys")
    print(f"\n5. Start services:")
    print(f"   docker-compose up -d")
    print(f"\n6. Initialize database:")
    print(f"   docker-compose exec backend alembic upgrade head")
    print(f"\n7. Test deployment:")
    print(f"   curl http://{SERVER}:8000/health")
    print(f"   curl http://{SERVER}:3000")

    # Try to at least copy the file
    print("\n[*] Attempting to copy file...")
    cmd = f'scp -o StrictHostKeyChecking=no gsr-deploy.tar.gz {USER}@{SERVER}:~/'
    print(f"Run this command:")
    print(f"  {cmd}")

    return True

def main():
    """Main deployment workflow"""
    print("=" * 60)
    print("GSR Analytics - Automated Deployment")
    print("=" * 60)
    print()

    # Step 1: Create package
    if not create_deployment_package():
        print("[-] Failed to create deployment package")
        return 1

    # Step 2: Deploy
    deploy_via_ssh()

    return 0

if __name__ == '__main__':
    sys.exit(main())
