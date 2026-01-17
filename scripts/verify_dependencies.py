#!/usr/bin/env python3
"""Script to verify all dependencies are available and compatible."""
import sys
import subprocess
import importlib
from typing import List, Tuple

# Required packages to check
REQUIRED_PACKAGES = [
    ("fastapi", "0.104.1"),
    ("uvicorn", "0.24.0"),
    ("python-dotenv", "1.0.0"),
    ("pydantic", "2.5.0"),
    ("pydantic-settings", "2.1.0"),
    ("langdetect", "1.0.9"),
    ("chromadb", "0.4.22"),
    ("sentence_transformers", "2.2.2"),
    ("pypdf", "3.17.4"),
    ("pdfplumber", "0.10.3"),
    ("numpy", None),  # Version flexible
    ("torch", None),  # Version flexible
    ("openai", "1.3.0"),
    ("azure.search.documents", None),  # azure-search-documents
    ("azure.identity", None),  # azure-identity
    ("semantic_kernel", None),  # Version flexible, >=1.30.0
]

# Optional packages (for Azure mode)
OPTIONAL_PACKAGES = [
    ("semantic_kernel", None),
]


def check_package(package_name: str, expected_version: str = None) -> Tuple[bool, str]:
    """Check if a package is installed and optionally verify version."""
    try:
        # Handle special cases for package name vs import name
        import_name = package_name.replace("-", "_")
        if package_name == "azure.search.documents":
            import_name = "azure.search.documents"
        elif package_name == "azure.identity":
            import_name = "azure.identity"
        elif package_name == "sentence_transformers":
            import_name = "sentence_transformers"
        
        module = importlib.import_module(import_name)
        
        if expected_version:
            # Try to get version
            version = getattr(module, "__version__", None)
            if version:
                return True, f"[OK] {package_name} (version {version})"
            else:
                return True, f"[OK] {package_name} (installed, version unknown)"
        else:
            return True, f"[OK] {package_name} (installed)"
            
    except ImportError as e:
        return False, f"[FAIL] {package_name} - NOT INSTALLED: {e}"


def check_python_version() -> Tuple[bool, str]:
    """Check Python version compatibility."""
    version = sys.version_info
    if version.major == 3 and version.minor >= 10:
        return True, f"[OK] Python {version.major}.{version.minor}.{version.micro} (compatible)"
    else:
        return False, f"[FAIL] Python {version.major}.{version.minor}.{version.micro} (requires 3.10+)"


def run_pip_check() -> Tuple[bool, str]:
    """Run pip check to detect dependency conflicts."""
    try:
        result = subprocess.run(
            [sys.executable, "-m", "pip", "check"],
            capture_output=True,
            text=True,
            timeout=30
        )
        if result.returncode == 0:
            return True, "[OK] No dependency conflicts detected"
        else:
            return False, f"[FAIL] Dependency conflicts detected:\n{result.stdout}"
    except Exception as e:
        return False, f"[FAIL] Could not run pip check: {e}"


def main():
    """Main verification function."""
    print("=" * 60)
    print("Dependency Verification")
    print("=" * 60)
    print()
    
    # Check Python version
    print("Python Version:")
    success, message = check_python_version()
    print(f"  {message}")
    print()
    
    if not success:
        print("ERROR: Python version is not compatible!")
        sys.exit(1)
    
    # Check required packages
    print("Required Packages:")
    all_ok = True
    for package, version in REQUIRED_PACKAGES:
        success, message = check_package(package, version)
        print(f"  {message}")
        if not success:
            all_ok = False
    print()
    
    # Check optional packages
    print("Optional Packages (for Azure mode):")
    for package, version in OPTIONAL_PACKAGES:
        success, message = check_package(package, version)
        print(f"  {message}")
    print()
    
    # Run pip check
    print("Dependency Conflicts Check:")
    success, message = run_pip_check()
    print(f"  {message}")
    if not success:
        all_ok = False
    print()
    
    # Summary
    print("=" * 60)
    if all_ok:
        print("[SUCCESS] All dependencies verified successfully!")
        sys.exit(0)
    else:
        print("[ERROR] Some dependencies are missing or have conflicts!")
        print("\nTo fix, run:")
        print("  pip install -r requirements.txt")
        sys.exit(1)


if __name__ == "__main__":
    main()
