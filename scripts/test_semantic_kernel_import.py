"""Test semantic kernel import."""
import sys
import os

# Fix Windows encoding issues
if sys.platform == 'win32':
    os.environ['PYTHONIOENCODING'] = 'utf-8'

print("Testing semantic-kernel import...")
try:
    import semantic_kernel as sk
    print(f"[OK] semantic_kernel imported successfully (version: {sk.__version__})")
    
    try:
        from semantic_kernel.connectors.ai.open_ai import AzureChatCompletion
        print("[OK] AzureChatCompletion imported successfully")
        print("\n[SUCCESS] All imports successful!")
    except ImportError as e:
        print(f"[ERROR] AzureChatCompletion import failed: {e}")
        print("\nChecking available modules...")
        try:
            import semantic_kernel.connectors.ai as ai_module
            print(f"Available in ai module: {dir(ai_module)}")
        except Exception as e2:
            print(f"Could not inspect ai module: {e2}")
        sys.exit(1)
        
except ImportError as e:
    print(f"[ERROR] semantic_kernel import failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
