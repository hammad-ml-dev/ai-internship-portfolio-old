#!/usr/bin/env python3
"""
Simple Launcher for Restaurant Lead Generation Pipeline
Provides a menu-driven interface for easy usage
"""

import os
import sys
import subprocess

def clear_screen():
    """Clear the console screen"""
    os.system('cls' if os.name == 'nt' else 'clear')

def show_menu():
    """Display the main menu"""
    print("=" * 60)
    print("🍕 RESTAURANT LEAD GENERATION PIPELINE")
    print("=" * 60)
    print("Choose an option:")
    print("1. 🧪 Run Quick Test (2 cities, 20 restaurants each)")
    print("2. 🚀 Run Full Pipeline (All cities)")
    print("3. 🏙️  Run Custom Cities")
    print("4. 📊 Check Output Files")
    print("5. 📋 View Logs")
    print("6. 🔧 Check System Status")
    print("7. ❓ Help")
    print("8. 🚪 Exit")
    print("=" * 60)

def run_quick_test():
    """Run the quick test pipeline"""
    print("\n🧪 Running Quick Test...")
    print("This will collect data from Karachi and Lahore (20 restaurants each)")
    print("Estimated time: 2-3 minutes")
    
    try:
        result = subprocess.run([sys.executable, "robust_pipeline.py", "--test"], 
                              capture_output=False, text=True)
        if result.returncode == 0:
            print("\n✅ Quick test completed successfully!")
        else:
            print("\n❌ Quick test failed!")
    except Exception as e:
        print(f"\n❌ Error running quick test: {e}")

def run_full_pipeline():
    """Run the full pipeline"""
    print("\n🚀 Running Full Pipeline...")
    print("This will collect data from all major Pakistani cities")
    print("Estimated time: 15-30 minutes")
    
    confirm = input("Are you sure you want to run the full pipeline? (y/n): ").lower()
    if confirm in ['y', 'yes']:
        try:
            result = subprocess.run([sys.executable, "robust_pipeline.py", "--full"], 
                                  capture_output=False, text=True)
            if result.returncode == 0:
                print("\n✅ Full pipeline completed successfully!")
            else:
                print("\n❌ Full pipeline failed!")
        except Exception as e:
            print(f"\n❌ Error running full pipeline: {e}")
    else:
        print("Full pipeline cancelled.")

def run_custom_cities():
    """Run pipeline with custom cities"""
    print("\n🏙️  Custom Cities Pipeline")
    print("Enter city names separated by commas (e.g., Karachi,Lahore,Islamabad)")
    
    cities_input = input("Cities: ").strip()
    if cities_input:
        cities = [city.strip() for city in cities_input.split(',')]
        print(f"\n🚀 Running pipeline for: {', '.join(cities)}")
        
        try:
            cmd = [sys.executable, "robust_pipeline.py", "--cities", cities_input]
            result = subprocess.run(cmd, capture_output=False, text=True)
            if result.returncode == 0:
                print("\n✅ Custom cities pipeline completed successfully!")
            else:
                print("\n❌ Custom cities pipeline failed!")
        except Exception as e:
            print(f"\n❌ Error running custom cities pipeline: {e}")
    else:
        print("No cities specified. Cancelled.")

def check_output_files():
    """Check what output files are available"""
    print("\n📊 Checking Output Files...")
    
    output_dir = "output"
    if os.path.exists(output_dir):
        files = os.listdir(output_dir)
        if files:
            print(f"Found {len(files)} output files:")
            for file in sorted(files, reverse=True):
                file_path = os.path.join(output_dir, file)
                size = os.path.getsize(file_path)
                print(f"  📄 {file} ({size} bytes)")
        else:
            print("No output files found.")
    else:
        print("Output directory not found.")
    
    # Check if there are any recent files
    recent_files = [f for f in files if f.endswith(('.csv', '.xlsx'))]
    if recent_files:
        print(f"\n📈 Total output files: {len(recent_files)}")
        print("💡 You can find these files in the 'output' folder")

def view_logs():
    """View recent log entries"""
    print("\n📋 Recent Log Entries...")
    
    log_file = "pipeline.log"
    if os.path.exists(log_file):
        try:
            with open(log_file, 'r', encoding='utf-8') as f:
                lines = f.readlines()
                if lines:
                    print("Last 20 log entries:")
                    for line in lines[-20:]:
                        print(f"  {line.strip()}")
                else:
                    print("Log file is empty.")
        except Exception as e:
            print(f"Error reading log file: {e}")
    else:
        print("No log file found.")

def check_system_status():
    """Check the system status"""
    print("\n🔧 System Status Check...")
    
    # Check Python version
    python_version = sys.version.split()[0]
    print(f"Python version: {python_version}")
    
    # Check if required files exist
    required_files = [
        "robust_pipeline.py",
        "start_pipeline.py", 
        "requirements.txt",
        "config.py"
    ]
    
    print("\nRequired files:")
    for file in required_files:
        if os.path.exists(file):
            print(f"  ✅ {file}")
        else:
            print(f"  ❌ {file} - MISSING")
    
    # Check directories
    required_dirs = ["models", "output", "logs"]
    print("\nRequired directories:")
    for directory in required_dirs:
        if os.path.exists(directory):
            print(f"  ✅ {directory}/")
        else:
            print(f"  ❌ {directory}/ - MISSING")
    
    # Check if we can import the pipeline
    try:
        from robust_pipeline import RobustRestaurantPipeline
        print("\n✅ Pipeline module can be imported successfully")
    except Exception as e:
        print(f"\n❌ Pipeline module import failed: {e}")

def show_help():
    """Show help information"""
    print("\n❓ Help & Information")
    print("=" * 40)
    print("This is a robust restaurant lead generation pipeline for Pakistan.")
    print("\n📖 How to use:")
    print("1. Choose 'Quick Test' for your first run")
    print("2. Use 'Full Pipeline' for comprehensive data collection")
    print("3. Use 'Custom Cities' for specific locations")
    print("4. Check 'Output Files' to see your results")
    print("5. View 'Logs' for detailed information")
    print("\n📁 Output files are saved in the 'output' folder")
    print("📋 Logs are saved in 'pipeline.log'")
    print("\n🚀 For advanced usage, use the command line:")
    print("   python robust_pipeline.py --help")

def main():
    """Main launcher function"""
    while True:
        clear_screen()
        show_menu()
        
        try:
            choice = input("\nEnter your choice (1-8): ").strip()
            
            if choice == '1':
                run_quick_test()
            elif choice == '2':
                run_full_pipeline()
            elif choice == '3':
                run_custom_cities()
            elif choice == '4':
                check_output_files()
            elif choice == '5':
                view_logs()
            elif choice == '6':
                check_system_status()
            elif choice == '7':
                show_help()
            elif choice == '8':
                print("\n👋 Goodbye! Thank you for using the Restaurant Lead Generation Pipeline!")
                break
            else:
                print("\n❌ Invalid choice. Please enter a number between 1 and 8.")
            
            input("\nPress Enter to continue...")
            
        except KeyboardInterrupt:
            print("\n\n👋 Pipeline interrupted. Goodbye!")
            break
        except Exception as e:
            print(f"\n❌ Unexpected error: {e}")
            input("Press Enter to continue...")

if __name__ == "__main__":
    main()
