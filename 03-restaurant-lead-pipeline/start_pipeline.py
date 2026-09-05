#!/usr/bin/env python3
"""
Startup Script for Restaurant Lead Generation Pipeline
Ensures all dependencies are available and runs the pipeline reliably
"""

import os
import sys
import subprocess
import importlib

def check_dependencies():
    """Check if all required packages are installed"""
    required_packages = [
        'pandas', 'numpy', 'requests', 'beautifulsoup4',
        'selenium', 'openpyxl', 'python-dotenv'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            importlib.import_module(package)
            print(f"✓ {package}")
        except ImportError:
            missing_packages.append(package)
            print(f"❌ {package} - MISSING")
    
    return missing_packages

def install_dependencies():
    """Install missing dependencies"""
    print("\nInstalling missing dependencies...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✓ Dependencies installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install dependencies: {e}")
        return False

def create_directories():
    """Create necessary directories"""
    directories = ['models', 'output', 'logs', 'temp']
    for directory in directories:
        os.makedirs(directory, exist_ok=True)
        print(f"✓ Directory ensured: {directory}")

def run_pipeline():
    """Run the robust pipeline"""
    print("\n🚀 Starting Restaurant Lead Generation Pipeline...")
    
    try:
        # Import and run the robust pipeline
        from robust_pipeline import RobustRestaurantPipeline
        
        pipeline = RobustRestaurantPipeline()
        
        # Run a test first
        print("🧪 Running test pipeline...")
        result = pipeline.run_test()
        
        if not result.empty:
            print(f"✅ Test successful! Generated {len(result)} leads")
            
            # Ask user if they want to run full pipeline
            response = input("\nDo you want to run the full pipeline? (y/n): ").lower()
            if response in ['y', 'yes']:
                print("🚀 Running full pipeline...")
                full_result = pipeline.run_pipeline()
                if not full_result.empty:
                    print(f"🎉 Full pipeline completed! Generated {len(full_result)} leads")
                else:
                    print("❌ Full pipeline failed")
            else:
                print("Test completed successfully!")
        else:
            print("❌ Test pipeline failed")
            
    except Exception as e:
        print(f"❌ Pipeline failed: {e}")
        import traceback
        traceback.print_exc()

def main():
    """Main startup function"""
    print("=" * 60)
    print("🍕 RESTAURANT LEAD GENERATION PIPELINE STARTUP")
    print("=" * 60)
    
    # Check dependencies
    print("Checking dependencies...")
    missing = check_dependencies()
    
    if missing:
        print(f"\nMissing packages: {', '.join(missing)}")
        response = input("Do you want to install missing dependencies? (y/n): ").lower()
        if response in ['y', 'yes']:
            if install_dependencies():
                print("✓ All dependencies are now available")
            else:
                print("❌ Failed to install dependencies. Please install manually:")
                print("pip install -r requirements.txt")
                return
        else:
            print("❌ Cannot proceed without required dependencies")
            return
    
    # Create directories
    print("\nSetting up directories...")
    create_directories()
    
    # Run pipeline
    run_pipeline()

if __name__ == "__main__":
    main()
