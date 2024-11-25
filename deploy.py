import os
import time

def display_process():
    # Use the environment variable if set, otherwise default to "Idle"
    current_process = os.getenv("CURRENT_PROCESS", "Idle")

    # Optionally, ask the user for input if no environment variable is set
    if current_process == "Idle":
        current_process = input("Enter the current process (default: Idle): ") or "Idle"

    # Display the process in a loop
    while True:
        print(f"Current Process: {current_process}")
        time.sleep(5)  # Updates every 5 seconds

if __name__ == "__main__":
    display_process()
