## Setup Instructions - SSH iOS Development Environment

### Step 1: Clone the Repository

Clone this repository to your local machine and navigate to the repository root.

### Step 2: Follow Initial Setup Instructions

Follow the steps in the [README.md](README.md) file to set up the environment and install macOS (Sonoma).

### Step 3: Initial VM Boot

Start the VM for the first time with the GUI to complete the initial macOS setup:

```bash
./OpenCore-Boot.sh
```

Complete the macOS setup and install XCode and other GUI-dependent tools.

**Note:** Active SSH on macOS `System Preferences > Sharing > Remote Login`.

### Step 4: Install XCode and Generate Unique Serial

If you need to install XCode, you'll need a unique serial number. Complete steps 1-5 below and start `./OpenCore-Boot.sh` again to connect to your Apple account, install XCode, and other tools.

```bash
# Download XCode from [Apple Developer](https://developer.apple.com/download/all/?q=xcode)
xip -x ~/Downloads/$xcode_version.xip -C /Applications

xcode-select --install
```

1. Navigate or clone GenSMBIOS repository into workspace:

    ```bash
    git clone https://github.com/corpnewt/GenSMBIOS.git
    cd GenSMBIOS
    ```

2. Make `GenSMBIOS.command` executable and run it:

    ```bash
    chmod +x GenSMBIOS.command
    ./GenSMBIOS.command
    ```

3. Install/Update MacSerial.
4. Select `$osx_kvm_path/OpenCore/headless/config.plist` as the configuration file.
5. Generate SMBIOS for `iMacPro1,1`.
6. Generate UUID.

### Step 5: Generate OpenCore Image with NoUI Configuration

```bash
# Update submodule
git submodule update --init --recursive ./resources/OcBinaryData

cd ./OpenCore

# Generate OpenCore image with NoUI configuration
rm -f OpenCore.qcow2; sudo ./opencore-image-ng.sh --cfg ./headless/config.plist --img OpenCore.qcow2
```

### Step 6: Start OpenCore VM with NoUI Configuration

```bash
# Navigate to repository root
cd $osx_kvm_path
# cd ..

# Make the shell script executable
chmod +x ./headless_boot.sh

./headless_boot.sh
```

### Step 7: Connect to macOS VM with SSH

```bash
ssh -p 2222 $user_name@localhost
```

### Step 8: Map Port 22 to 2222 and Open Firewall

```bash
# Map port 22 to 2222
sudo iptables -t nat -A PREROUTING -p tcp --dport 22 -j REDIRECT --to-port 2222

# Open firewall
sudo iptables -A INPUT -p tcp --dport 22 -j ACCEPT
```

### Step 9: Connect from Any Device on the Network to the VM

```bash
ssh $user_name@$vm_host_ip
```

### Step 10: Shutdown the VM

```bash
# (run on mac via SSH)
sudo shutdown -h now
```

## Additional Notes

When you use the VSCode Remote SSH extension, you will disconnect from the VM as soon as the VM enters sleep mode. To prevent this, you can enable automatic login and disable lock screen in the macOS settings. This way, the user will be logged in automatically when the VM starts and won't enter sleep mode.

I personally use Nix flakes to manage the environment, so I can install all the required tools with `nix develop` and run the scripts from there. (The Nix package manager does not support XCode, so you need to install it manually first.)

Additionally, I use GitHub to store my credentials, which allows me to just copy the `.gitconfig` and `.git-credentials` to the user home directory on the VM.

To debug iOS apps, it's easiest to use XCode Wi-Fi debugging, so you don't need to connect the phone to the VM.

### Install as a Service

To install the VM as a service, you can run the `headless_service_install.sh` script. This script will install the VM as a service that starts on boot.

```bash
chmod +x ./headless_service_install.sh

./headless_service_install.sh
```

#### Uninstall Service

Run the commands below to uninstall the service:

```bash
sudo systemctl stop headless_opencore.service

sudo systemctl disable headless_opencore.service

sudo rm /etc/systemd/system/headless_opencore.service

sudo systemctl daemon-reload
```
