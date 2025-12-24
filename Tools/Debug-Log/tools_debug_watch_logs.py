"""Real-time log file monitoring script"""
import time
import os

log_file = r"d:\Projets\Python\DAOC---Gestion-des-personnages\Logs\debug.log"

print("=" * 70)
print("REAL-TIME LOG FILE MONITORING")
print("=" * 70)
print(f"\nMonitored file: {log_file}")
print("\nINSTRUCTIONS:")
print("1. Leave this script running")
print("2. Launch the application (F5 in VS Code)")
print("3. Logs will appear here in real-time")
print("4. Press Ctrl+C to stop monitoring")
print("\n" + "-" * 70)
print("Waiting for logs...\n")

# Create the file if it does not exist
if not os.path.exists(log_file):
    open(log_file, 'w').close()

# Current position in the file
last_position = 0

try:
    with open(log_file, 'r', encoding='utf-8', errors='ignore') as f:
        # Go to the end of the file
        f.seek(0, 2)
        last_position = f.tell()
        
        while True:
            # Read new lines
            f.seek(last_position)
            new_lines = f.read()
            
            if new_lines:
                # Display relevant lines with color coding
                for line in new_lines.strip().split('\n'):
                    if any(keyword in line for keyword in [
                        'REALM_ICONS', 'Verification', 'tree_realm_icons',
                        'Populating tree', 'Icon loading', 'icon found', 
                        'Pre-loading', 'Application starting'
                    ]):
                        print(f">>> {line}")
                    elif 'ERROR' in line or 'WARNING' in line or 'CRITICAL' in line:
                        print(f"!!! {line}")
                    elif 'DEBUG' in line:
                        print(f"... {line}")
                    
                last_position = f.tell()
            
            time.sleep(0.5)
            
except KeyboardInterrupt:
    print("\n\n" + "-" * 70)
    print("Monitoring stopped.")
    print("-" * 70)
