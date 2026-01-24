#!/usr/bin/env python3
"""
Quick Fix Script - Enable Missing Framework Tools
Automatically installs or verifies missing tools for maximum framework support
"""

import subprocess
import sys
import os
import platform

class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    END = '\033[0m'
    BOLD = '\033[1m'

def print_status(msg, status='info'):
    """Print colored status message"""
    colors = {
        'success': Colors.GREEN,
        'error': Colors.RED,
        'warning': Colors.YELLOW,
        'info': Colors.BLUE
    }
    symbol = {
        'success': '✅',
        'error': '❌',
        'warning': '⚠️ ',
        'info': 'ℹ️ '
    }
    print(f"{colors.get(status, Colors.BLUE)}{symbol.get(status, '')} {msg}{Colors.END}")

def run_command(cmd, shell=False):
    """Run command and return success status"""
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, shell=shell)
        return result.returncode == 0, result.stdout + result.stderr
    except Exception as e:
        return False, str(e)

def check_tool(tool_name, check_cmd=None):
    """Check if a tool is available"""
    if check_cmd is None:
        check_cmd = f"{tool_name} --version"
    
    success, output = run_command(check_cmd, shell=True)
    return success, output

def install_expo_cli():
    """Install Expo CLI globally"""
    print_status(f"\n{Colors.BOLD}Installing Expo CLI...{Colors.END}")
    
    success, output = run_command("npm install -g expo-cli", shell=True)
    
    if success:
        print_status("Expo CLI installed successfully", 'success')
        # Verify installation
        success, output = check_tool("expo")
        if success:
            print_status(f"Verified: {output.strip()}", 'success')
            return True
    else:
        print_status(f"Failed to install Expo CLI: {output}", 'error')
    return False

def check_cargo():
    """Check Cargo installation and availability"""
    print_status(f"\n{Colors.BOLD}Checking Cargo/Rust...{Colors.END}")
    
    # Check if cargo exists
    success, output = check_tool("cargo")
    if success:
        print_status(f"Cargo found: {output.strip()}", 'success')
        return True
    
    # Check if rustup is available
    success, output = check_tool("rustup")
    if success:
        print_status("Rustup found - adding cargo to PATH...", 'warning')
        print_status("Please run: rustup update", 'info')
        print_status("Or download from: https://rustup.rs/", 'info')
        return False
    
    print_status("Cargo/Rust not found", 'error')
    print_status("Download from: https://rustup.rs/", 'info')
    return False

def check_java():
    """Check Java installation"""
    print_status(f"\n{Colors.BOLD}Checking Java...{Colors.END}")
    
    success, output = check_tool("java", "java -version")
    
    if success:
        print_status(f"Java found:\n{output.strip()}", 'success')
        return True
    
    print_status("Java Development Kit (JDK) not found", 'error')
    print_status("Download from: https://www.oracle.com/java/technologies/downloads/", 'info')
    return False

def check_flutter():
    """Check Flutter installation"""
    print_status(f"\n{Colors.BOLD}Checking Flutter...{Colors.END}")
    
    success, output = check_tool("flutter")
    
    if success:
        print_status(f"Flutter found: {output.strip()}", 'success')
        return True
    
    print_status("Flutter SDK not found", 'error')
    print_status("Download from: https://flutter.dev/docs/get-started/install", 'info')
    return False

def print_summary(results):
    """Print summary of installation results"""
    print(f"\n{Colors.BOLD}{'='*60}")
    print(f"FRAMEWORK TOOLS STATUS SUMMARY")
    print(f"{'='*60}{Colors.END}\n")
    
    total = len(results)
    success_count = sum(1 for v in results.values() if v)
    
    for tool, status in results.items():
        symbol = '✅' if status else '❌'
        print(f"{symbol} {tool:20} {'READY' if status else 'MISSING'}")
    
    print(f"\n{Colors.BOLD}Total: {success_count}/{total} Tools Ready ({int(100*success_count/total)}%){Colors.END}\n")
    
    return success_count, total

def suggest_next_steps(results):
    """Suggest next steps based on results"""
    print(f"{Colors.BOLD}NEXT STEPS:{Colors.END}\n")
    
    missing = [k for k, v in results.items() if not v]
    
    if not missing:
        print_status("All tools are available! Ready to build all frameworks.", 'success')
        return
    
    if 'Expo CLI' in missing:
        print("1️⃣  Install Expo CLI:")
        print("   npm install -g expo-cli")
        print("   (1-2 minutes, enables Expo framework)\n")
    
    if 'Cargo' in missing:
        print("2️⃣  Install/Verify Cargo:")
        print("   Download from: https://rustup.rs/")
        print("   (5-10 minutes, enables Tauri framework)\n")
    
    if 'Java' in missing:
        print("3️⃣  Install Java Development Kit:")
        print("   Download from: https://www.oracle.com/java/technologies/downloads/")
        print("   Set JAVA_HOME environment variable")
        print("   (20 minutes, enables Flutter, React Native, Ionic, NativeScript)\n")

def main():
    """Main execution"""
    print(f"\n{Colors.BOLD}{Colors.BLUE}")
    print("╔════════════════════════════════════════════════════════════════╗")
    print("║        GAAIUS-AI FRAMEWORK TOOLS QUICK FIX                     ║")
    print("║        Check & Install Missing Framework Tools                 ║")
    print("╚════════════════════════════════════════════════════════════════╝")
    print(f"{Colors.END}\n")
    
    # Check all tools
    results = {}
    
    print_status("Checking installed tools...\n", 'info')
    
    # Check Expo CLI
    success, _ = check_tool("expo")
    results['Expo CLI'] = success
    if success:
        print_status("✅ Expo CLI is installed", 'success')
    else:
        print_status("❌ Expo CLI not found", 'error')
    
    # Check Cargo
    success, _ = check_tool("cargo")
    results['Cargo'] = success
    if success:
        print_status("✅ Cargo is installed", 'success')
    else:
        print_status("❌ Cargo not found", 'error')
    
    # Check Java
    success, _ = check_tool("java", "java -version")
    results['Java'] = success
    if success:
        print_status("✅ Java is installed", 'success')
    else:
        print_status("❌ Java not found", 'error')
    
    # Check Flutter
    success, _ = check_tool("flutter")
    results['Flutter'] = success
    if success:
        print_status("✅ Flutter is installed", 'success')
    else:
        print_status("❌ Flutter not found", 'error')
    
    # Print summary
    success_count, total = print_summary(results)
    
    # Suggest next steps
    suggest_next_steps(results)
    
    # Ask to install Expo CLI if missing
    if not results['Expo CLI']:
        response = input(f"{Colors.BOLD}Install Expo CLI now? (y/n): {Colors.END}").strip().lower()
        if response == 'y':
            install_expo_cli()
    
    print(f"\n{Colors.BOLD}For more details, see: FRAMEWORK_TOOLS_AUDIT_REPORT.md{Colors.END}\n")

if __name__ == '__main__':
    main()
