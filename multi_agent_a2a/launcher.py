#!/usr/bin/env python3
"""
Multi-Agent A2A System Launcher

This script helps you start the multi-agent system components.
It can start both servers and then run the client.
"""

import subprocess
import sys
import time
import os
import signal
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

def start_server(script_name, port, agent_name):
    """Start a server process"""
    print(f"Starting {agent_name} server on port {port}...")
    process = subprocess.Popen([
        sys.executable, script_name
    ], cwd=Path(__file__).parent)
    
    # Give the server a moment to start
    time.sleep(2)
    return process


def check_requirements():
    """Check if required environment variables are set"""
    required_vars = ["OPENAI_API_KEY", "GITHUB_ACCESS_TOKEN"]
    missing_vars = []
    
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        print("❌ Missing required environment variables:")
        for var in missing_vars:
            print(f"   - {var}")
        print("\nPlease set these environment variables and try again.")
        return False
    
    print("✅ All required environment variables are set")
    return True


def main():
    """Main launcher function"""
    print("🚀 Multi-Agent A2A System Launcher")
    print("=" * 50)
    
    # Check requirements
    if not check_requirements():
        sys.exit(1)
    
    print("\nOptions:")
    print("1. Start both servers and run demo")
    print("2. Start both servers and run interactive client")
    print("3. Start only lights server")
    print("4. Start only GitHub server")
    print("5. Run client only (servers must be running)")
    print("6. Exit")
    
    choice = input("\nChoose an option (1-6): ").strip()
    
    processes = []
    
    try:
        if choice == "1":
            # Start both servers
            lights_process = start_server("lights_server.py", 8001, "Lights")
            processes.append(lights_process)
            
            github_process = start_server("github_server.py", 8002, "GitHub")
            processes.append(github_process)
            
            print("✅ Both servers started successfully!")
            print("\nRunning demo client...")
            time.sleep(2)
            
            # Run demo client
            demo_env = os.environ.copy()
            subprocess.run([sys.executable, "client.py", "demo"], env=demo_env)
                         
        elif choice == "2":
            # Start both servers
            lights_process = start_server("lights_server.py", 8001, "Lights")
            processes.append(lights_process)
            
            github_process = start_server("github_server.py", 8002, "GitHub")
            processes.append(github_process)
            
            print("✅ Both servers started successfully!")
            print("\nStarting interactive client...")
            time.sleep(2)
            
            # Run interactive client
            interactive_env = os.environ.copy()
            subprocess.run([sys.executable, "client.py", "interactive"], env=interactive_env)
                         
        elif choice == "3":
            lights_process = start_server("lights_server.py", 8001, "Lights")
            processes.append(lights_process)
            print("✅ Lights server started! Press Ctrl+C to stop.")
            
            # Keep the process running
            try:
                lights_process.wait()
            except KeyboardInterrupt:
                pass
                
        elif choice == "4":
            github_process = start_server("github_server.py", 8002, "GitHub")
            processes.append(github_process)
            print("✅ GitHub server started! Press Ctrl+C to stop.")
            
            # Keep the process running
            try:
                github_process.wait()
            except KeyboardInterrupt:
                pass
                
        elif choice == "5":
            print("🔗 Running client (make sure servers are running)...")
            subprocess.run([sys.executable, "client.py"])
            
        elif choice == "6":
            print("👋 Goodbye!")
            return
            
        else:
            print("❌ Invalid choice")
            return
            
    except KeyboardInterrupt:
        print("\n\n🛑 Stopping servers...")
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        # Clean up processes
        for process in processes:
            try:
                process.terminate()
                process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                process.kill()
            except:
                pass
        
        if processes:
            print("✅ All servers stopped")


if __name__ == "__main__":
    main()
