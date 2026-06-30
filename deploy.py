#!/usr/bin/env python3

import subprocess
import os
import sys
from dotenv import load_dotenv

load_dotenv()

def check_vercel():
    """Check if Vercel CLI is installed"""
    try:
        subprocess.run(["vercel", "--version"], check=True, capture_output=True)
        return True
    except:
        return False

def check_git():
    """Check if Git is installed"""
    try:
        subprocess.run(["git", "--version"], check=True, capture_output=True)
        return True
    except:
        return False

def check_env():
    """Check if .env file exists and has required variables"""
    if not os.path.exists(".env"):
        print("❌ .env file not found!")
        print("   Create .env from .env.example:")
        print("   cp .env.example .env")
        return False
    
    required = ["BOT_TOKEN", "SUPABASE_URL", "SUPABASE_KEY", "WEBHOOK_URL"]
    
    for var in required:
        if not os.environ.get(var):
            print(f"❌ {var} not set in .env")
            return False
    
    return True

def install_vercel():
    """Install Vercel CLI"""
    print("📦 Installing Vercel CLI...")
    try:
        if sys.platform == "win32":
            subprocess.run(["npm", "install", "-g", "vercel"], check=True)
        else:
            subprocess.run(["sudo", "npm", "install", "-g", "vercel"], check=True)
        print("✅ Vercel CLI installed")
        return True
    except Exception as e:
        print(f"❌ Failed to install Vercel: {e}")
        return False

def deploy():
    """Deploy to Vercel"""
    print("🚀 Deploying to Vercel...")
    try:
        subprocess.run(["vercel", "--prod"], check=True)
        print("✅ Deployment successful!")
        return True
    except Exception as e:
        print(f"❌ Deployment failed: {e}")
        return False

def setup_webhook():
    """Setup webhook after deployment"""
    print("🔌 Setting up webhook...")
    try:
        subprocess.run([sys.executable, "setup_webhook.py"], check=True)
        print("✅ Webhook setup complete!")
        return True
    except Exception as e:
        print(f"❌ Webhook setup failed: {e}")
        return False

def main():
    """Main deployment flow"""
    print("╔════════════════════════════════╗")
    print("║  NomadShare Vercel Deployment  ║")
    print("╚════════════════════════════════╝\n")
    
    # Check prerequisites
    print("📋 Checking prerequisites...")
    
    if not check_git():
        print("❌ Git is not installed")
        return False
    print("✅ Git installed")
    
    if not check_vercel():
        print("⚠️  Vercel CLI not installed")
        if not install_vercel():
            return False
    else:
        print("✅ Vercel CLI installed")
    
    if not check_env():
        return False
    print("✅ Environment variables set")
    
    # Deploy
    print("\n🚀 Starting deployment...\n")
    if not deploy():
        return False
    
    # Setup webhook
    print("\n🔌 Setting up webhook...\n")
    if not setup_webhook():
        print("⚠️  Webhook setup failed, but deployment was successful")
        print("   Run 'python setup_webhook.py' to setup webhook manually")
    
    print("\n" + "="*50)
    print("✅ Deployment complete!")
    print("="*50)
    print("\nBot is now running on Vercel!")
    print("Webhook URL: " + os.environ.get("WEBHOOK_URL", "Not set"))
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
