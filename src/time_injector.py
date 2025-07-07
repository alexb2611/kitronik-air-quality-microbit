#!/usr/bin/env python3
"""
Time Injector Script for BBC micro:bit RTC Projects
Automatically updates main.py with current time before flashing

This script finds the time injection point in main.py and updates it
with the current system time, eliminating manual time entry.

Usage:
1. python time_injector.py main.py
2. Flash the updated main.py to your micro:bit
3. Your RTC will be set automatically!

Author: Alex's BBC micro:bit Project
"""

import datetime
import re
import os
import sys

def inject_current_time(file_path):
    """
    Inject current system time into micro:bit Python code
    
    Args:
        file_path (str): Path to the main.py file
    
    Returns:
        bool: True if successful, False otherwise
    """
    
    if not os.path.exists(file_path):
        print(f"❌ Error: File '{file_path}' not found!")
        return False
    
    # Get current time
    now = datetime.datetime.now()
    
    print(f"🕐 Injecting current time: {now.strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Read the file
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Find the injection point
    injection_pattern = r'(# === AUTO TIME INJECTION POINT ===.*?)(current_year\s*=\s*\d+)(.*?)(current_month\s*=\s*\d+)(.*?)(current_day\s*=\s*\d+)(.*?)(current_hour\s*=\s*\d+)(.*?)(current_minute\s*=\s*\d+)(.*?)(current_second\s*=\s*\d+)(.*?)(# === END INJECTION POINT ===)'
    
    # Replacement with current time
    def replace_time_values(match):
        return (
            match.group(1) +  # Comment
            f"current_year = {now.year}" +
            match.group(3) +  # Whitespace/comment
            f"current_month = {now.month}" +
            match.group(5) +  # Whitespace/comment
            f"current_day = {now.day}" +
            match.group(7) +  # Whitespace/comment
            f"current_hour = {now.hour}" +
            match.group(9) +  # Whitespace/comment
            f"current_minute = {now.minute}" +
            match.group(11) + # Whitespace/comment
            f"current_second = {now.second}" +
            match.group(13) + # Whitespace/comment
            match.group(14)   # End comment
        )
    
    # Apply the replacement
    updated_content = re.sub(injection_pattern, replace_time_values, content, flags=re.DOTALL)
    
    # Check if replacement was successful
    if updated_content == content:
        print("⚠️  Warning: No time injection point found in file")
        print("   Make sure your main.py has the AUTO TIME INJECTION POINT markers")
        return False
    
    # Create backup
    backup_path = file_path + ".backup"
    with open(backup_path, 'w', encoding='utf-8') as f:
        f.write(content)
    print(f"💾 Backup created: {backup_path}")
    
    # Write updated file
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(updated_content)
    
    print(f"✅ Time injected successfully into {file_path}")
    print(f"🚀 Ready to flash to micro:bit!")
    
    # Show what was injected
    print(f"\n📅 Injected values:")
    print(f"   Year:   {now.year}")
    print(f"   Month:  {now.month}")
    print(f"   Day:    {now.day}")
    print(f"   Hour:   {now.hour}")
    print(f"   Minute: {now.minute}")
    print(f"   Second: {now.second}")
    
    return True

def main():
    """Main entry point"""
    print("🔬 BBC micro:bit Time Injector")
    print("=" * 40)
    
    # Get file path from command line or use default
    if len(sys.argv) > 1:
        file_path = sys.argv[1]
    else:
        file_path = "main.py"
    
    print(f"📁 Target file: {file_path}")
    
    # Inject time
    success = inject_current_time(file_path)
    
    if success:
        print("\n🎉 Success! Next steps:")
        print("1. Flash the updated main.py to your micro:bit")
        print("2. Insert micro:bit into Kitronik Air Quality Board")
        print("3. Power on - RTC will be set automatically!")
        print("\n💡 Your micro:bit will show:")
        print("   ❤️  → Starting up")
        print("   🕐 → Setting RTC time") 
        print("   ✅  → RTC set successfully")
        print("   📊 → Environmental monitoring begins")
    else:
        print("\n❌ Failed to inject time. Please check the error messages above.")
        sys.exit(1)

if __name__ == "__main__":
    main()
