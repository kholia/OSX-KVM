

### How to setup your MacOS VM in Google compute cloud (GCP)

My macOS journey to the cloud begins...
AWS has a bare metal macOS instance that cost $950 a month fixed price, at this price I can buy one Mac every month!!

AFAIK AWS doesn't have any VM instances that support netsted virtualization :(
GCP has instances that support nested virtualization

Setup procedure:
1. Launch an Ubuntu 22.04 n1-standard-8 VM with a 100GB SSD drive.
   This server is oversized so we can speedup the install, later we can shrink it.
``` 
#!/bin/bash

VM_NAME=ubuntu-nested
DISKSIZE=202
DISKTYPE=pd-ssd
MACHINETYPE=c2-standard-8
IMAGE=projects/ubuntu-os-cloud/global/images/ubuntu-2204-jammy-v20220609
ZONE=some-zone
PROJECT=my-project

gcloud compute instances create $VM_NAME \
  --machine-type=$MACHINETYPE \
  --enable-nested-virtualization \
  --zone=$ZONE --project=$PROJECT \
  --boot-disk-size=$DISKSIZE --image=$IMAGE --boot-disk-type=$DISKTYPE \
  --min-cpu-platform="Intel Haswell"

gcloud compute ssh $VM_NAME --project=$PROJECT --zone=$ZONE
```

2. Setup VNC on your instance, follow this guide:
   https://www.digitalocean.com/community/tutorials/how-to-install-and-configure-vnc-on-ubuntu-20-04
3. Configure your VNC client to use full color
4. Connect to your new insance via VNC and complete the install via VNC connection
5. Configure your nested VM to use 8GB RAM:
```sed -i s/4096/8192/ OpenCore-Boot.sh```
6. A few more configurations:
``` sudo apt install -y xterm ; sudo chmod 666 /dev/kvm```
7. Run the installer 
```./OpenCore-Boot.sh```

When you erase the disk leave the name of the disk as "Untitled".
There is a problem with the Qemu keyboard so you MUST configure the on-screen keyboard to be active during the MacOS install process AND on the MacOS login screen.

To activate the on-screen keyboard during the install process select "Motor" from this screen:

<a href="url"><img src="https://github.com/AAber/OSX-KVM/blob/gcp/screenshots/Motor.png" align="center" height="530" ></a>

Then enable the on-screen keyboard:

<a href="url"><img src="https://github.com/AAber/OSX-KVM/blob/gcp/screenshots/AccessibilityKeyboard.png" align="center" height="500" ></a>

See this link for details on enabling the on-screen keyboard on the MacOS login screen:
https://support.apple.com/en-il/guide/mac-help/mchlaa57f797/mac#:~:text=Anyone%20who%20logs%20in%20to,display%20the%20Accessibility%20Shortcuts%20panel.
![Login screen On-screen keyboard](https://github.com/AAber/OSX-KVM/blob/gcp/screenshots/LoginKeyboard.png)

## Warning:
If you don't have the on-screen keyboard on your new Mac login screen you will be locked out from your cloud Mac.
After you configure the keyboard on-screen I recommend you install AnyDesk remote access tool and connect to your new cloud Mac via AnyDesk.

I tested TeamViewer and it failed for me.
AnyDesk works well.
Others may also work.

Ping me if you have any questions.

I like this note:
Add notes from Constantin Jacob.
Note: This pretty much violates everything hardware-wise in the macOS EULA that
one could violate.
