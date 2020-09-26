# ansible
> an Ansible playbook for configuring a Linux KVM host to run macOS VM(s)

## ToC

* [deploy Linux host](#deploy-linux-host)
* [setup Ansible](#setup-ansible)
* [create Ansible inventory](#create-ansible-inventory)
* [test connectivity](#test-connectivity)
* [run playbook](#run-playbook)


## deploy Linux host
> deploy a Linux host to run macOS virtual machine(s)

* deploy `Ubuntu 20.04 LTS` on a suitable piece of hardware
* ⚠️ bridge Ethernet adapter to `br0` interface (e.g. with [netplan](https://fabianlee.org/2019/04/01/kvm-creating-a-bridged-network-with-netplan-on-ubuntu-bionic/) or `cloud-config`)

```
#cloud-config
autoinstall:
  version: 1
  network:
    network:
      ethernets:
        id0:
          match:
            name: en*
      version: 2

      bridges:
        br0:
          interfaces: [id0]
          dhcp4: true
          dhcp6: true
          parameters:
            stp: yes
            forward-delay: 4
  ...
```

* note down its `{{ ipaddr }}` to be used in the inventory file


## setup Ansible
> configure Ansible tooling on a suitable macOS or Linux workstation

    python3 -m venv venv3

    . venv3/bin/activate

    pip3 install -r requirements.txt --upgrade


## create Ansible inventory
> substitute your Ubuntu Linux host `{{ ipaddr }}`

```
inventory_file=$(mktemp)

cat << EOF > ${inventory_file}
[linux]
{{ ipaddr }}
EOF
```

## test connectivity
> ensure your workstation can connect to the Linux host via SSH and sudo is configured appropriately [for Ansible](https://docs.ansible.com/ansible/latest/user_guide/become.html)

    cat ${inventory_file}

    ansible -vi ${inventory_file} linux -m ping --become


## run playbook

	ansible-playbook --verbose \
	  --inventory ${inventory_file} site.yml \
	  --tags osx-kvm
