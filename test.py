import subprocess
import platform
from datetime import datetime

def run_command(cmd: list[str]) -> tuple[bool, str]:
    """
    Executes an OS command using standard subprocess library.
    Returns (success status, output string).
    """
    print(f"   -> Executing OS Command: {' '.join(cmd)}")
    try:
        # Run the command and capture stdout/stderr
        result = subprocess.run(
            cmd, 
            capture_output=True, 
            text=True, 
            check=True, # Raise error if the command fails
            encoding='utf-8'
        )
        return True, result.stdout
    except subprocess.CalledProcessError as e:
        # Command ran but failed (e.g., permission denied)
        return False, f"Command Failed:\n{e.stderr}"
    except FileNotFoundError:
        # The command itself doesn't exist on this system
        return False, "ERROR: Required utility not found on this system."
    except Exception as e:
        return False, f"An unexpected error occurred: {e}"

def collect_network_config():
    """
    Collects detailed network configuration based on the operating system.
    Requires elevated privileges (sudo/Administrator) for full output.
    """
    print("=" * 60)
    print("📡 NETWORK CONFIGURATION GATHERER")
    print(f"📅 Run Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("-" * 60)

    system = platform.system()
    config_data = {"System OS": system, "Details": ""}

    if system == "Windows":
        # Standard Windows command to show all IP details (including MAC addresses)
        command = ["ipconfig", "/all"]
        success, output = run_command(command)
        config_data["Network Config Output"] = f"--- Successfully Collected (Check for detailed Ethernet/Wireless adapters below) ---\n{output}\n\n*** NOTE: You may need to run the script with 'sudo' or as Administrator. ***"

    elif system == "Linux":
        # The modern, comprehensive Linux tool
        command = ["ip", "addr", "show"]
        success, output = run_command(command)
        config_data["Network Config Output"] = f"--- Successfully Collected (Requires root privileges for full detail) ---\n{output}\n\n*** NOTE: You may need to run the script using 'sudo'. ***"

    elif system == "Darwin": # macOS uses Darwin/BSD naming conventions
        # The standard command on macOS
        command = ["ifconfig"]
        success, output = run_command(command)
        config_data["Network Config Output"] = f"--- Successfully Collected (Requires root privileges for full detail) ---\n{output}\n\n*** NOTE: You may need to run the script using 'sudo'. ***"

    else:
        config_data["Network Config Output"] = "Unsupported Operating System. Please check platform support."

    # --- Display Results ---
    print("\n" * 2)
    print("=" * 60)
    print("✅ CONFIGURATION SUMMARY COMPLETE")
    print(f"System: {config_data['System OS']}")
    print("-" * 60)
    print("\n--- RAW OUTPUT DATA ---\n")
    # Print the full collected output block
    print(config_data["Network Config Output"])


if __name__ == "__main__":
    collect_network_config()

