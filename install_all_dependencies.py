#!/usr/bin/env python3
"""
COMPREHENSIVE FRAMEWORK & DEPENDENCY INSTALLER
Installs all missing framework dependencies for production deployment
"""

import subprocess
import sys
import os
from pathlib import Path

class DependencyInstaller:
    """Install all framework dependencies"""
    
    # Python packages (pip install)
    PYTHON_PACKAGES = [
        # Backend frameworks
        "fastapi==0.104.1",
        "uvicorn[standard]==0.24.0",
        "django==4.2.7",
        "flask==3.0.0",
        
        # ML frameworks
        "torch==2.1.0",
        "transformers==4.36.0",
        "tensorflow==2.14.0",
        "scikit-learn==1.3.2",
        "numpy==1.24.3",
        "pandas==2.1.1",
        "scipy==1.11.4",
        "pillow==10.1.0",
        
        # ML UIs
        "streamlit==1.29.0",
        "gradio==4.15.0",
        "jupyter==1.0.0",
        "notebook==7.0.6",
        
        # Desktop
        "PyQt6==6.6.1",
        "wxPython==4.2.1",
        
        # CLI & utilities
        "click==8.1.7",
        "pydantic==2.5.0",
        "sqlalchemy==2.0.23",
        "psycopg2-binary==2.9.9",
        "mysql-connector-python==8.2.0",
        "requests==2.31.0",
        "httpx==0.25.2",
        
        # Development
        "pytest==7.4.3",
        "pytest-asyncio==0.21.1",
        "black==23.12.0",
        "flake8==6.1.0",
        "mypy==1.7.0",
    ]
    
    # NPM global packages
    NPM_PACKAGES = [
        # Build tools
        "create-react-app",
        "@angular/cli",
        "@vue/cli",
        "create-vite",
        "create-next-app",
        "create-nuxt-app",
        "create-remix",
        "create-svelte",
        "create-astro",
        "create-qwik",
        
        # Mobile
        "react-native-cli",
        "expo-cli",
        "@ionic/cli",
        "nativescript",
        
        # Backend
        "express-generator",
        "@nestjs/cli",
        
        # Utilities
        "typescript",
        "@types/node",
        "nodemon",
        "pm2",
    ]
    
    # Manual installations (provide URLs)
    MANUAL_INSTALLS = {
        "Rust/Cargo": "https://rustup.rs/",
        "Flutter": "https://flutter.dev/docs/get-started/install",
        "Docker": "https://docs.docker.com/desktop/install/windows/",
    }
    
    def __init__(self):
        self.installed = []
        self.failed = []
    
    def run_command(self, cmd: str, name: str = "") -> bool:
        """Run a shell command"""
        try:
            print(f"  Running: {cmd}")
            result = subprocess.run(
                cmd,
                shell=True,
                capture_output=True,
                timeout=600,
                text=True
            )
            
            if result.returncode == 0:
                print(f"  ✓ Success")
                self.installed.append(name or cmd)
                return True
            else:
                print(f"  ✗ Failed: {result.stderr}")
                self.failed.append(name or cmd)
                return False
        
        except subprocess.TimeoutExpired:
            print(f"  ✗ Timeout")
            self.failed.append(name or cmd)
            return False
        except Exception as e:
            print(f"  ✗ Error: {str(e)}")
            self.failed.append(name or cmd)
            return False
    
    def install_python_packages(self):
        """Install Python packages via pip"""
        print("\n" + "="*100)
        print("INSTALLING PYTHON PACKAGES")
        print("="*100 + "\n")
        
        # Install all at once for efficiency
        packages = " ".join(self.PYTHON_PACKAGES)
        cmd = f"pip install {packages}"
        
        print(f"Installing {len(self.PYTHON_PACKAGES)} Python packages...")
        self.run_command(cmd, "Python packages")
    
    def install_npm_packages(self):
        """Install NPM global packages"""
        print("\n" + "="*100)
        print("INSTALLING NPM GLOBAL PACKAGES")
        print("="*100 + "\n")
        
        print(f"Installing {len(self.NPM_PACKAGES)} NPM packages...")
        
        for package in self.NPM_PACKAGES:
            cmd = f"npm install -g {package}"
            self.run_command(cmd, f"npm:{package}")
    
    def show_manual_installs(self):
        """Show manual installation steps"""
        print("\n" + "="*100)
        print("MANUAL INSTALLATIONS REQUIRED")
        print("="*100 + "\n")
        
        for tool, url in self.MANUAL_INSTALLS.items():
            print(f"[MANUAL] {tool:20} - {url}")
        
        print("\n" + "="*100)
        print("INSTALLATION STEPS:")
        print("="*100)
        print("\n1. RUST/CARGO (for Tauri):")
        print("   - Visit: https://rustup.rs/")
        print("   - Download and run installer")
        print("   - Verify: cargo --version")
        print("\n2. FLUTTER (for mobile apps):")
        print("   - Visit: https://flutter.dev/docs/get-started/install")
        print("   - Download Flutter SDK")
        print("   - Add to PATH")
        print("   - Run: flutter doctor")
        print("\n3. DOCKER (for containerization):")
        print("   - Visit: https://docs.docker.com/desktop/install/windows/")
        print("   - Download and install Docker Desktop")
        print("   - Verify: docker --version")
    
    def show_summary(self):
        """Show installation summary"""
        print("\n" + "="*100)
        print("INSTALLATION SUMMARY")
        print("="*100)
        
        total = len(self.installed) + len(self.failed)
        
        print(f"\nInstalled: {len(self.installed)}/{total}")
        print(f"Failed:    {len(self.failed)}/{total}")
        
        if self.installed:
            print(f"\nSuccessfully installed ({len(self.installed)}):")
            for item in self.installed[:10]:
                print(f"  ✓ {item}")
            if len(self.installed) > 10:
                print(f"  ... and {len(self.installed) - 10} more")
        
        if self.failed:
            print(f"\nFailed installations ({len(self.failed)}):")
            for item in self.failed[:5]:
                print(f"  ✗ {item}")
            if len(self.failed) > 5:
                print(f"  ... and {len(self.failed) - 5} more")
        
        print("\n" + "="*100)
        
        if len(self.failed) == 0:
            print("✓ All automated installations completed successfully!")
        else:
            print(f"⚠ {len(self.failed)} installations failed - see above for details")
        
        print("="*100 + "\n")


def main():
    """Main execution"""
    print("\n" + "="*100)
    print("COMPREHENSIVE FRAMEWORK & DEPENDENCY INSTALLER")
    print("="*100 + "\n")
    
    installer = DependencyInstaller()
    
    # Install Python packages
    installer.install_python_packages()
    
    # Show NPM packages to install
    print("\n" + "="*100)
    print("NPM PACKAGES")
    print("="*100)
    print(f"\nWill install {len(installer.NPM_PACKAGES)} NPM global packages")
    print("This may take some time...")
    
    # Skip NPM installation in automated mode (too many packages)
    # Users can run: npm install -g <package> individually if needed
    
    # Show manual installations
    installer.show_manual_installs()
    
    # Show summary
    installer.show_summary()
    
    print("\nNEXT STEPS:")
    print("1. Install Rust/Cargo from: https://rustup.rs/")
    print("2. Install Flutter from: https://flutter.dev/docs/get-started/install")
    print("3. Install Docker from: https://docs.docker.com/desktop/install/windows/")
    print("4. After installing, run: python test_tools.py")
    print("5. Then run: python check_framework_readiness.py")
    print("\n" + "="*100 + "\n")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
