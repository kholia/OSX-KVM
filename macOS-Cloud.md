

### How to setup you MacOS VM in Google compute cloud (GCP)

I started my macOS journey to the cloud a week or so ago, AWS has a bare metal macOS instance that cost $950 a month fixed price, at this price I can buy one Mac every month!!

So I wanted to setup a Mac in the cloud for our QA team.

AFAIK AWS doesn't have any instance that support netsted virtualization :(
GCP has instances that support nested virtualization

Setup procedure:
1. Launch an Ubuntu 22.04 n1-standard-8 VM with a 100GB SSD drive.
   This server is oversized so we can speedup the install.
`` 
!/bin/bash

VM_NAME=ubuntu-nested
DISKSIZE=100
MACHINETYPE=n1-standard-8
IMAGE=projects/ubuntu-os-cloud/global/images/ubuntu-2204-jammy-v20220609
ZONE=some-zone
PROJECT=my-project

gcloud compute instances create $VM_NAME \
  --machine-type=$MACHINETYPE \
  --enable-nested-virtualization \
  --zone=$ZONE --project=$PROJECT \
  --boot-disk-size=$DISKSIZE --image=$IMAGE \
  --min-cpu-platform="Intel Haswell"

gcloud compute ssh $VM_NAME-nested --project=$PROJECT --zone=$ZONE

# Cleanup
# gcloud compute instances delete ubuntu-nested --project=$PROJECT --zone=$ZONE

2. Setup VNC on your instance, follow this guide:
https://www.digitalocean.com/community/tutorials/how-to-install-and-configure-vnc-on-ubuntu-20-04
3. Configure you VNC client to use full color

4. Connect to your new insance via VNC and complete the install via VNC connection
5. Configure your nested VM to use 8GB RAM:

``
sed -i s/4096/8192/ OpenCore-Boot.sh

6. A few more configurations:
`` sudo apt install -y xterm ; sudo chmod 666 /dev/kvm

7. Run the installer ./OpenCore-Boot.sh

There is a problem with the Qemu keyboard so you will need to configure the on screen keyboard for install and login screen.
When you earase the disk leave the name of the disk as "Untitled"
See this link for details on enabling the on screen keyboard at the login screen:
https://support.apple.com/en-il/guide/mac-help/mchlaa57f797/mac#:~:text=Anyone%20who%20logs%20in%20to,display%20the%20Accessibility%20Shortcuts%20panel.

Warning:
If you don't have the on-screen keyboard on your new Mac login screen you will be locked out from your cloud Mac. 
After you configure the keyboard on screen I recommend you install Anydesk remote access tool and connect to your new cloud Mac.

I tested Teamviewer and it failed for me.
Anydesk works well.
Others may also work.





I like this note:
Add notes from Constantin Jacob.
Note: This pretty much violates everything hardware-wise in the macOS EULA that
one could violate.