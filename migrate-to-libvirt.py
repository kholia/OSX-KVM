#!/usr/bin/env python3
"""Copy a stopped OSX-KVM installation into local system libvirt storage."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import uuid
import xml.etree.ElementTree as ET

BASE = Path(__file__).resolve().parent
URI = 'qemu:///system'
NS = 'http://libvirt.org/schemas/domain/qemu/1.0'
ET.register_namespace('qemu', NS)
CPU_FLAGS = ('-hle,-rtm,kvm=on,vendor=GenuineIntel,+invtsc,'
             'vmware-cpuid-freq=on,+ssse3,+sse4.2,+popcnt,+avx,+aes,'
             '+xsave,+xsaveopt,check')


def parser():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--name', default='macOS')
    p.add_argument('--disk', type=Path, default=BASE / 'mac_hdd_ng.img')
    p.add_argument('--opencore', type=Path, default=BASE / 'OpenCore/OpenCore.qcow2')
    p.add_argument('--firmware-code', type=Path, default=BASE / 'OVMF_CODE_4M.fd')
    p.add_argument('--firmware-vars', type=Path, default=BASE / 'OVMF_VARS-1920x1080.fd')
    p.add_argument('--pool', default='default')
    p.add_argument('--nvram-pool', default='nvram')
    p.add_argument('--ram', type=int, default=4096, help='RAM in MiB')
    p.add_argument('--cpu-model', default='Skylake-Client')
    p.add_argument('--sockets', type=int, default=1)
    p.add_argument('--cores', type=int, default=2)
    p.add_argument('--threads', type=int, default=2)
    p.add_argument('--ssh-port', type=int, default=2222)
    p.add_argument('--output-dir', type=Path)
    p.add_argument('--dry-run', action='store_true')
    p.add_argument('--yes', action='store_true', help='skip import confirmation')
    p.add_argument('--start', action='store_true', help='start after successful registration')
    return p


def validate_args(a):
    if not re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9_.-]{0,63}', a.name):
        raise ValueError('Name must contain only letters, numbers, dots, underscores or hyphens.')
    if not re.fullmatch(r'[A-Za-z0-9_.-]+', a.cpu_model):
        raise ValueError('Invalid CPU model.')
    if min(a.ram, a.sockets, a.cores, a.threads) <= 0:
        raise ValueError('RAM and CPU topology must be positive.')
    if not 1024 <= a.ssh_port <= 65535:
        raise ValueError('SSH port must be between 1024 and 65535.')
    a.output_dir = (a.output_dir or Path.home() / '.local/share/osx-kvm-imports' / a.name).resolve()
    if a.output_dir.exists():
        raise ValueError(f'Output directory already exists: {a.output_dir}')


def image_info(path):
    # No -U: respect QEMU image locks instead of inspecting an active writer.
    result = subprocess.run(['qemu-img', 'info', '--output=json', str(path)],
                            check=True, capture_output=True, text=True)
    info = json.loads(result.stdout)
    if info.get('backing-filename') or info.get('full-backing-filename'):
        raise ValueError(f'Backing chains are unsupported: {path}')
    return info


def fingerprint(path):
    s = path.stat()
    return (s.st_dev, s.st_ino, s.st_size, s.st_mtime_ns, s.st_ctime_ns)


def pool_details(conn, name):
    pool = conn.storagePoolLookupByName(name)
    root = ET.fromstring(pool.XMLDesc(0))
    if root.get('type') != 'dir' or not pool.isActive():
        raise ValueError(f'Pool {name!r} must be an active directory pool.')
    return pool, Path(root.findtext('./target/path'))


def prepare(conn, a):
    if a.name in [d.name() for d in conn.listAllDomains(0)]:
        raise ValueError(f'Domain already exists: {a.name}')
    pool, target = pool_details(conn, a.pool)
    nvpool, nvtarget = pool_details(conn, a.nvram_pool)
    items = []
    for role, source, suffix, destpool, directory in [
        ('disk', a.disk, '.qcow2', pool, target),
        ('opencore', a.opencore, '-OpenCore.qcow2', pool, target),
        ('code', a.firmware_code, '-OVMF_CODE.fd', pool, target),
        ('vars', a.firmware_vars, '_VARS.fd', nvpool, nvtarget),
    ]:
        source = source.resolve(strict=True)
        if not source.is_file() or not os.access(source, os.R_OK):
            raise ValueError(f'Not a readable file: {source}')
        name = a.name + suffix
        if name in destpool.listVolumes():
            raise ValueError(f'Volume already exists: {directory / name}')
        info = image_info(source)
        expected = 'qcow2' if role in ('disk', 'opencore') else 'raw'
        if info.get('format') != expected:
            raise ValueError(f'{source}: expected {expected}, found {info.get("format")}')
        items.append(dict(role=role, source=source, name=name, pool=destpool,
                          path=directory / name, before=fingerprint(source)))
    sources = {str(i['source']) for i in items}
    for domain in conn.listAllDomains(0):
        root = ET.fromstring(domain.XMLDesc(0))
        refs = [n.get('file') for n in root.findall('./devices/disk/source')]
        refs += [root.findtext('./os/loader'), root.findtext('./os/nvram')]
        if any(str(Path(p).resolve()) in sources for p in refs if p):
            raise ValueError(f'Source files are already referenced by domain {domain.name()}.')
    # Pools can share one filesystem: sum their requirements rather than checking separately.
    required = {}
    for item in items:
        directory = item['path'].parent
        device = directory.stat().st_dev
        required.setdefault(device, [directory, 0])[1] += item['before'][2]
    for directory, size in required.values():
        if shutil.disk_usage(directory).free < size + 64 * 1024 * 1024:
            raise ValueError(f'Insufficient free space on {directory}')
    return items


def domain_xml(a, items):
    r = ET.parse(BASE / 'resources/libvirt-migration.xml').getroot()
    r.find('name').text = a.name
    ET.SubElement(r, 'uuid').text = str(uuid.uuid4())
    for tag in ('memory', 'currentMemory'):
        r.find(tag).set('unit', 'MiB')
        r.find(tag).text = str(a.ram)
    r.find('vcpu').text = str(a.sockets * a.cores * a.threads)
    r.find('./cpu/model').text = a.cpu_model
    topology = r.find('./cpu/topology')
    topology.attrib = dict(sockets=str(a.sockets), cores=str(a.cores), threads=str(a.threads))
    paths = {i['role']: str(i['path']) for i in items}
    r.find('./os/loader').text = paths['code']
    r.find('./os/nvram').text = paths['vars']
    disks = r.findall('./devices/disk/source')
    disks[0].set('file', paths['opencore'])
    disks[1].set('file', paths['disk'])
    mac = '52:54:00:' + ':'.join(f'{b:02x}' for b in os.urandom(3))
    args = r.findall(f'./{{{NS}}}commandline/{{{NS}}}arg')
    for n, arg in enumerate(args):
        value = arg.get('value', '')
        if value == '-cpu':
            args[n + 1].set('value', a.cpu_model + ',' + CPU_FLAGS)
        if value.startswith('user,id='):
            arg.set('value', f'user,id=macosnet,hostfwd=tcp:127.0.0.1:{a.ssh_port}-:22')
        if value.startswith('virtio-net-pci,'):
            arg.set('value', f'virtio-net-pci,netdev=macosnet,mac={mac},bus=pcie.0,addr=0x5')
    ET.indent(r, space='  ')
    return ET.tostring(r, encoding='unicode')


def volume_xml(item):
    root = ET.Element('volume')
    ET.SubElement(root, 'name').text = item['name']
    ET.SubElement(root, 'capacity', unit='bytes').text = str(item['before'][2])
    target = ET.SubElement(root, 'target')
    # Upload the container bytes unchanged, then refresh for QCOW2 detection.
    ET.SubElement(target, 'format', type='raw')
    permissions = ET.SubElement(target, 'permissions')
    ET.SubElement(permissions, 'mode').text = '0644' if item['role'] == 'code' else '0600'
    return ET.tostring(root, encoding='unicode')


def upload_verify(conn, volume, item):
    source = item['source']
    stream = conn.newStream(0)
    digest = hashlib.sha256()
    try:
        volume.upload(stream, 0, item['before'][2], 0)
        with source.open('rb') as f:
            while chunk := f.read(1024 * 1024):
                digest.update(chunk)
                offset = 0
                while offset < len(chunk):
                    sent = stream.send(chunk[offset:])
                    if sent <= 0:
                        raise RuntimeError('Upload made no progress')
                    offset += sent
        stream.finish()
    except BaseException:
        stream.abort()
        raise
    if fingerprint(source) != item['before']:
        raise RuntimeError(f'Source changed during import: {source}')
    downloaded = hashlib.sha256()
    stream = conn.newStream(0)
    try:
        volume.download(stream, 0, item['before'][2], 0)
        while chunk := stream.recv(1024 * 1024):
            downloaded.update(chunk)
        stream.finish()
    except BaseException:
        stream.abort()
        raise
    if digest.digest() != downloaded.digest():
        raise RuntimeError(f'Checksum mismatch: {item["name"]}')
    return digest.hexdigest()


def migrate(conn, a, items, xml):
    created = []
    registered = False
    a.output_dir.mkdir(parents=True, exist_ok=False)
    try:
        # This dedicated blocking Python connection does not enable client keepalive.
        summary = []
        for item in items:
            image_info(item['source'])  # Recheck locks after interactive confirmation.
            if fingerprint(item['source']) != item['before']:
                raise RuntimeError(f'Source changed: {item["source"]}')
            print(f'Importing and verifying {item["source"]} -> {item["path"]}', flush=True)
            volume = item['pool'].createXML(volume_xml(item), 0)
            created.append(volume)
            checksum = upload_verify(conn, volume, item)
            item['pool'].refresh(0)
            summary.append(dict(source=str(item['source']), destination=str(item['path']), sha256=checksum))
        (a.output_dir / 'domain.xml').write_text(xml + '\n')
        (a.output_dir / 'import.json').write_text(json.dumps(summary, indent=2) + '\n')
        domain = conn.defineXML(xml)
        registered = True
        (a.output_dir / 'domain.xml').write_text(domain.XMLDesc(2) + '\n')
        print(f'Registered {a.name}. Open Virtual Machine Manager using {URI}.')
        print('Original files retained. The old boot script starts an independent disk copy.')
        if a.start:
            domain.create()
    except BaseException:
        if not registered:
            for volume in reversed(created):
                try:
                    volume.delete(0)
                except Exception as error:
                    print(f'Cleanup failed for {volume.name()}: {error}', file=sys.stderr)
            print(f'Import failed; diagnostic output retained at {a.output_dir}', file=sys.stderr)
        else:
            print('VM is registered and its files are retained; inspect the start failure.', file=sys.stderr)
        raise


def main():
    a = parser().parse_args()
    conn = None
    try:
        validate_args(a)
        if not shutil.which('qemu-img'):
            raise ValueError('Install qemu-img (qemu-utils on Debian/Ubuntu).')
        try:
            import libvirt
        except ImportError:
            raise ValueError('Install Python libvirt bindings (python3-libvirt on Debian/Ubuntu).') from None
        conn = libvirt.open(URI)
        items = prepare(conn, a)
        xml = domain_xml(a, items)
        conn.domainXMLToNative('qemu-argv', xml, 0)
        print(xml, flush=True)
        if a.dry_run:
            print('Dry run: no files or VM definitions changed.')
            return 0
        print('Shut down the source VM and keep it stopped throughout the import.')
        if not a.yes and input('Copy, verify and register this VM? [y/N] ').lower() != 'y':
            return 0
        migrate(conn, a, items, xml)
        return 0
    except (Exception, KeyboardInterrupt) as error:
        print(f'Import failed: {error}', file=sys.stderr)
        return 1
    finally:
        if conn is not None:
            conn.close()


if __name__ == '__main__':
    sys.exit(main())
