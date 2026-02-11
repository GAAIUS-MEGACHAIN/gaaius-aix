#!/usr/bin/env python3
"""
FRAMEWORK TOOLS AUDIT - Check which tools are installed for each framework
Comprehensive analysis of framework requirements vs. available tools
"""

import subprocess
import sys

FRAMEWORK_REQUIREMENTS = {
    # DESKTOP FRAMEWORKS
    "Tauri": {
        "category": "Desktop",
        "tools": {
            "rustc": "Rust compiler",
            "cargo": "Rust package manager",
        },
        "required_for_build": True,
        "optional": False
    },
    "Electron": {
        "category": "Desktop",
        "tools": {
            "node": "Node.js",
            "npm": "NPM",
        },
        "required_for_build": True,
        "optional": False
    },
    "PyQt6": {
        "category": "Desktop",
        "tools": {
            "python": "Python",
            "pip": "PIP",
        },
        "required_for_build": True,
        "optional": False
    },
    "wxPython": {
        "category": "Desktop",
        "tools": {
            "python": "Python",
            "pip": "PIP",
        },
        "required_for_build": True,
        "optional": False
    },

    # MOBILE FRAMEWORKS
    "Flutter": {
        "category": "Mobile",
        "tools": {
            "flutter": "Flutter SDK",
            "dart": "Dart SDK",
            "java": "Java (Android)",
        },
        "required_for_build": True,
        "optional": False
    },
    "React Native": {
        "category": "Mobile",
        "tools": {
            "node": "Node.js",
            "npm": "NPM",
            "java": "Java (Android)",
        },
        "required_for_build": True,
        "optional": False
    },
    "Expo": {
        "category": "Mobile",
        "tools": {
            "node": "Node.js",
            "npm": "NPM",
            "expo": "Expo CLI",
        },
        "required_for_build": True,
        "optional": False
    },
    "Ionic": {
        "category": "Mobile",
        "tools": {
            "node": "Node.js",
            "npm": "NPM",
            "java": "Java (Android)",
        },
        "required_for_build": True,
        "optional": False
    },
    "NativeScript": {
        "category": "Mobile",
        "tools": {
            "node": "Node.js",
            "npm": "NPM",
            "java": "Java (Android)",
        },
        "required_for_build": True,
        "optional": False
    },

    # WEB FRAMEWORKS
    "React": {
        "category": "Web",
        "tools": {
            "node": "Node.js",
            "npm": "NPM",
        },
        "required_for_build": True,
        "optional": False
    },
    "Angular": {
        "category": "Web",
        "tools": {
            "node": "Node.js",
            "npm": "NPM",
        },
        "required_for_build": True,
        "optional": False
    },
    "Vue": {
        "category": "Web",
        "tools": {
            "node": "Node.js",
            "npm": "NPM",
        },
        "required_for_build": True,
        "optional": False
    },
    "Svelte": {
        "category": "Web",
        "tools": {
            "node": "Node.js",
            "npm": "NPM",
        },
        "required_for_build": True,
        "optional": False
    },
    "Vite": {
        "category": "Web",
        "tools": {
            "node": "Node.js",
            "npm": "NPM",
        },
        "required_for_build": True,
        "optional": False
    },
    "Next.js": {
        "category": "Web",
        "tools": {
            "node": "Node.js",
            "npm": "NPM",
        },
        "required_for_build": True,
        "optional": False
    },
    "Nuxt": {
        "category": "Web",
        "tools": {
            "node": "Node.js",
            "npm": "NPM",
        },
        "required_for_build": True,
        "optional": False
    },
    "Remix": {
        "category": "Web",
        "tools": {
            "node": "Node.js",
            "npm": "NPM",
        },
        "required_for_build": True,
        "optional": False
    },
    "SvelteKit": {
        "category": "Web",
        "tools": {
            "node": "Node.js",
            "npm": "NPM",
        },
        "required_for_build": True,
        "optional": False
    },
    "Astro": {
        "category": "Web",
        "tools": {
            "node": "Node.js",
            "npm": "NPM",
        },
        "required_for_build": True,
        "optional": False
    },
    "Qwik": {
        "category": "Web",
        "tools": {
            "node": "Node.js",
            "npm": "NPM",
        },
        "required_for_build": True,
        "optional": False
    },
    "SolidStart": {
        "category": "Web",
        "tools": {
            "node": "Node.js",
            "npm": "NPM",
        },
        "required_for_build": True,
        "optional": False
    },

    # BACKEND FRAMEWORKS
    "FastAPI": {
        "category": "Backend",
        "tools": {
            "python": "Python",
            "pip": "PIP",
        },
        "required_for_build": True,
        "optional": False
    },
    "Django": {
        "category": "Backend",
        "tools": {
            "python": "Python",
            "pip": "PIP",
        },
        "required_for_build": True,
        "optional": False
    },
    "Flask": {
        "category": "Backend",
        "tools": {
            "python": "Python",
            "pip": "PIP",
        },
        "required_for_build": True,
        "optional": False
    },
    "Express": {
        "category": "Backend",
        "tools": {
            "node": "Node.js",
            "npm": "NPM",
        },
        "required_for_build": True,
        "optional": False
    },
    "NestJS": {
        "category": "Backend",
        "tools": {
            "node": "Node.js",
            "npm": "NPM",
        },
        "required_for_build": True,
        "optional": False
    },

    # ML/DATA FRAMEWORKS
    "Streamlit": {
        "category": "ML/Data",
        "tools": {
            "python": "Python",
            "pip": "PIP",
        },
        "required_for_build": True,
        "optional": False
    },
    "Gradio": {
        "category": "ML/Data",
        "tools": {
            "python": "Python",
            "pip": "PIP",
        },
        "required_for_build": True,
        "optional": False
    },
    "Jupyter": {
        "category": "ML/Data",
        "tools": {
            "python": "Python",
            "pip": "PIP",
        },
        "required_for_build": True,
        "optional": False
    },
}

class ToolAuditor:
    def __init__(self):
        self.available_tools = {}
        self.missing_frameworks = {}
        self.ready_frameworks = {}
        self.category_status = {}

    def check_tool(self, tool: str) -> bool:
        """Check if a tool is available in PATH"""
        try:
            result = subprocess.run(
                f"{tool} --version",
                shell=True,
                capture_output=True,
                timeout=5,
                text=True
            )
            return result.returncode == 0
        except:
            return False

    def audit(self):
        """Run full audit"""
        print("\n" + "="*100)
        print("FRAMEWORK TOOLS AUDIT - CHECKING REQUIREMENTS")
        print("="*100 + "\n")

        # First, check all available tools
        print("STEP 1: Checking Available Tools")
        print("-" * 100)
        
        tools_to_check = set()
        for fw, config in FRAMEWORK_REQUIREMENTS.items():
            for tool in config["tools"].keys():
                tools_to_check.add(tool)

        for tool in sorted(tools_to_check):
            is_available = self.check_tool(tool)
            self.available_tools[tool] = is_available
            status = "✓" if is_available else "✗"
            print(f"{status} {tool:15} - {'AVAILABLE' if is_available else 'MISSING'}")

        # Now check frameworks
        print("\n\nSTEP 2: Checking Frameworks Against Required Tools")
        print("-" * 100 + "\n")

        for framework, config in sorted(FRAMEWORK_REQUIREMENTS.items()):
            category = config["category"]
            tools = config["tools"]
            
            # Check if all required tools are available
            all_tools_available = all(
                self.available_tools.get(tool, False)
                for tool in tools.keys()
            )

            # Organize by category
            if category not in self.category_status:
                self.category_status[category] = {
                    "ready": [],
                    "missing": []
                }

            if all_tools_available:
                status = "✓ READY"
                self.ready_frameworks[framework] = config
                self.category_status[category]["ready"].append(framework)
                print(f"✓ {framework:20} READY")
            else:
                status = "✗ MISSING TOOLS"
                missing = [t for t in tools.keys() if not self.available_tools.get(t, False)]
                self.missing_frameworks[framework] = {
                    "config": config,
                    "missing_tools": missing
                }
                self.category_status[category]["missing"].append(framework)
                missing_str = ", ".join(missing)
                print(f"✗ {framework:20} MISSING: {missing_str}")

    def show_summary(self):
        """Show audit summary"""
        print("\n\n" + "="*100)
        print("AUDIT SUMMARY")
        print("="*100)

        total_frameworks = len(FRAMEWORK_REQUIREMENTS)
        ready_count = len(self.ready_frameworks)
        missing_count = len(self.missing_frameworks)

        print(f"\nTotal Frameworks: {total_frameworks}")
        print(f"Ready: {ready_count} ({ready_count*100//total_frameworks}%)")
        print(f"Missing Tools: {missing_count} ({missing_count*100//total_frameworks}%)")

        # By category
        print(f"\n\nBY CATEGORY:")
        print("-" * 100)
        for category in sorted(self.category_status.keys()):
            status = self.category_status[category]
            total = len(status["ready"]) + len(status["missing"])
            ready = len(status["ready"])
            print(f"\n{category:20} ({ready}/{total} ready)")
            
            if status["ready"]:
                for fw in status["ready"]:
                    print(f"  ✓ {fw}")
            
            if status["missing"]:
                for fw in status["missing"]:
                    tools = self.missing_frameworks[fw]["missing_tools"]
                    print(f"  ✗ {fw:15} - Missing: {', '.join(tools)}")

        # Missing tools summary
        print(f"\n\nMISSING TOOLS THAT BLOCK FRAMEWORKS:")
        print("-" * 100)
        
        blocked_by = {}
        for fw, info in self.missing_frameworks.items():
            for tool in info["missing_tools"]:
                if tool not in blocked_by:
                    blocked_by[tool] = []
                blocked_by[tool].append(fw)

        if blocked_by:
            for tool, frameworks in sorted(blocked_by.items()):
                fw_list = ", ".join(frameworks)
                print(f"\n{tool:15} (Missing)")
                print(f"  Blocks: {fw_list}")
                
                # Installation instructions
                if tool == "cargo":
                    print(f"  Install: https://rustup.rs/")
                elif tool == "flutter":
                    print(f"  Install: https://flutter.dev/docs/get-started/install")
                elif tool == "java":
                    print(f"  Install: Java Development Kit (Android requirement)")
                elif tool == "dart":
                    print(f"  Install: Comes with Flutter SDK")
                elif tool == "expo":
                    print(f"  Install: npm install -g expo-cli")
        else:
            print("No missing tools! All required tools are available.")

    def show_available_tools(self):
        """Show available tools"""
        print(f"\n\nAVAILABLE TOOLS:")
        print("-" * 100)
        
        for tool, available in sorted(self.available_tools.items()):
            if available:
                print(f"✓ {tool:15} - INSTALLED")

    def show_installation_commands(self):
        """Show installation commands for missing frameworks"""
        print(f"\n\nINSTALLATION COMMANDS FOR MISSING FRAMEWORKS:")
        print("-" * 100)
        
        if not self.missing_frameworks:
            print("All frameworks have required tools!")
            return

        print("\nTo get all frameworks working, install these missing tools:\n")

        commands = set()
        
        for fw, info in self.missing_frameworks.items():
            for tool in info["missing_tools"]:
                if tool == "cargo":
                    commands.add("# Rust/Cargo - Install from https://rustup.rs/")
                elif tool == "flutter":
                    commands.add("# Flutter - Install from https://flutter.dev/")
                elif tool == "java":
                    commands.add("# Java SDK - Required for Android development")

        for cmd in sorted(commands):
            print(cmd)


def main():
    auditor = ToolAuditor()
    auditor.audit()
    auditor.show_summary()
    auditor.show_available_tools()
    auditor.show_installation_commands()
    
    print("\n" + "="*100 + "\n")


if __name__ == "__main__":
    main()
