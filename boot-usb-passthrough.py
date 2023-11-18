import subprocess
import os
import signal
import time
import re

verbose_log = False

def initialize():
    # Check if the /tmp/udevadm_output file exists and delete it if necessary
    if os.path.exists("/tmp/udevadm_output"):
        os.remove("/tmp/udevadm_output")

    # Reload udev rules
    # subprocess.run(["udevadm", "control", "--reload-rules"])
    # subprocess.run(["udevadm", "trigger"])

def scan_udevadm():
    return subprocess.Popen(["udevadm", "monitor", "--environment", "--subsystem-match=usb", "--property"],
                            stdout=open("/tmp/udevadm_output", "w"))

def show_added_usb_devices(udevadm_pid):
    global verbose_log

    input("Now, insert the USB device. Press Enter when done.")
    time.sleep(3)
    os.kill(udevadm_pid, signal.SIGINT)

    # Show results in the desired format
    if verbose_log:
        print("Results of udevadm scan:")
        with open("/tmp/udevadm_output", "r") as file:
            print(file.read())

def extract_information():
    global verbose_log

    add_action = "ACTION=add"
    usb_devices = set()
    additional_settings = ""

    # Extract information blocks about the new USB device
    with open("/tmp/udevadm_output", "r") as file:
        info_blocks = file.read()

    if info_blocks:
        info_blocks = info_blocks.split("\n\n")
        info_blocks = [block for block in info_blocks if add_action in block and 'UDEV' in block]

        # Print complete blocks if necessary
        if verbose_log:
            print("Complete blocks of information about the inserted USB device:")
            print(info_blocks)

        print("\nInformation about the inserted USB devices:")
        for i, new_usb in enumerate(info_blocks):
            if 'DEVNAME' in new_usb:
                devname = [item.split('=')[1] for item in new_usb.split() if 'DEVNAME' in item][0]

                # Extract additional information
                hostbus = [item.split('=')[1] for item in new_usb.split() if 'BUSNUM' in item][0]
                hostaddr = [item.split('=')[1] for item in new_usb.split() if 'DEVNUM' in item][0]
                id_model = [item.split('=')[1] for item in new_usb.split() if 'ID_MODEL' in item]
                id_vendor = [item.split('=')[1] for item in new_usb.split() if 'ID_VENDOR' in item]
                id_fs_size = [item.split('=')[1] for item in new_usb.split() if 'ID_FS_SIZE' in item]

                # Print general information about the USB device
                print(f"==== Device #{i} ====")
                print(f"USB Host {hostbus}:{hostaddr}")
                if id_model:
                    print(f"Model: {id_model[0]}")
                if id_vendor:
                    print(f"Manufacturer: {id_vendor[0]}")
                if id_fs_size:
                    print(f"Size: {id_fs_size[0]}")

                print("\n")

                # Add the line to be added to the boot-macOS.sh script
                usb_devices.add(f"-device usb-host,hostdevice={devname}")

        additional_settings = "-device qemu-xhci,id=xhci-usb\n" + "\n".join(usb_devices)

        print("additionalSettings to pass to qemu:")
        print(additional_settings)
    else:
        print("No information available about the new USB device.")

    return additional_settings

def check_open_core_boot_file(additional_settings):
    global verbose_log

    file_path = "OpenCore-Boot.sh"
    # file_path = "boot-passthrough.sh"

    if os.path.exists(file_path):
        choice = input(f"\n\nThe file {file_path} exists. Start it with USB Passthrough? (Y/n)")
        if choice == "" or choice.lower().startswith("y"):
            with open(file_path, "r") as file:
                start_script = file.read()

            if start_script:
                # Insert additional_settings before the closing parenthesis of args
                start_script = re.sub(r'(\n\))', rf'\n  {additional_settings}\1', start_script, flags=re.DOTALL)

                if verbose_log:
                    print(start_script)

                print("Starting macOS...\n\n\n")
                execute_bash_script(start_script)

    else:
        print(f"The file {file_path} does not exist.")

def execute_bash_script(script):
    # Create a process to execute the bash script
    process = subprocess.Popen(['bash'], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

    # Write the script to the process's stdin
    stdout, stderr = process.communicate(input=script)

    # Print the output and any potential errors
    print("==== QEMU Output ====")
    print(stdout)

    if stderr:
        print("\n\n\n==== QEMU ERROR ====")
        print(stderr)

def clean_up():
    print("\n\nRemoving temporary files...")
    os.remove("/tmp/udevadm_output")

def main():
    print("Preparation phase...")

    # Initialization
    initialize()

    # Perform the initial udevadm scan
    udevadm_pid = scan_udevadm().pid

    # Display a message and wait for user input
    show_added_usb_devices(udevadm_pid)

    # Extract information and print the line for the boot-macOS.sh script
    additional_settings = extract_information()

    # Execute exit procedures
    clean_up()

    check_open_core_boot_file(additional_settings)

    print("\n\nExiting... Goodbye!")

main()
