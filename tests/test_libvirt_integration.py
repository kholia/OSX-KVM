"""Opt-in local system-libvirt tests using only temporary pools and new domains.

Run with OSX_KVM_LIBVIRT_TESTS=1 /usr/bin/python3 -m unittest discover -s tests -v
No guest is started and no existing domain or pool is modified.
"""
import hashlib
import os
from pathlib import Path
import subprocess
import shutil
import time
import tempfile
import unittest
from unittest.mock import MagicMock, patch
import uuid
import xml.etree.ElementTree as ET

from test_libvirt_migration import m


@unittest.skipUnless(os.environ.get('OSX_KVM_LIBVIRT_TESTS') == '1',
                     'set OSX_KVM_LIBVIRT_TESTS=1 for isolated local libvirt tests')
class LibvirtIntegrationTests(unittest.TestCase):
    def setUp(self):
        import libvirt
        self.libvirt = libvirt
        self.conn = libvirt.open(m.URI)
        self.addCleanup(self.conn.close)
        self.root = Path(tempfile.mkdtemp(prefix='osx-kvm-review-'))
        self.retain_resources = False
        self.addCleanup(lambda: None if self.retain_resources else shutil.rmtree(self.root))
        destination = self.root / 'pool'
        destination.mkdir()
        self.name = 'osx-kvm-review-' + uuid.uuid4().hex[:12]
        xml = ET.Element('pool', type='dir')
        ET.SubElement(xml, 'name').text = self.name
        ET.SubElement(ET.SubElement(xml, 'target'), 'path').text = str(destination)
        self.pool = self.conn.storagePoolCreateXML(ET.tostring(xml, encoding='unicode'), 0)
        self.addCleanup(self.cleanup_libvirt)
        sources = {}
        for role in ('disk', 'opencore', 'code', 'vars'):
            path = self.root / role
            if role in ('disk', 'opencore'):
                subprocess.run(['qemu-img', 'create', '-f', 'qcow2', str(path), '8M'],
                               check=True, capture_output=True)
            else:
                path.write_bytes(b'\0' * 4096)
            sources[role] = path
        self.args = m.parser().parse_args([
            '--name', self.name, '--pool', self.name, '--nvram-pool', self.name,
            '--disk', str(sources['disk']), '--opencore', str(sources['opencore']),
            '--firmware-code', str(sources['code']), '--firmware-vars', str(sources['vars']),
            '--output-dir', str(self.root / 'output')])
        m.validate_args(self.args)
        self.originals = {p: p.read_bytes() for p in sources.values()}

    def cleanup_libvirt(self):
        domains = [d for d in self.conn.listAllDomains(0) if d.name() == self.name]
        for domain in domains:
            # These tests never start a VM. Do not force-stop anything unexpectedly running.
            if domain.isActive():
                self.retain_resources = True
                raise RuntimeError('Unexpected active test domain; retaining its resources')
            domain.undefineFlags(self.libvirt.VIR_DOMAIN_UNDEFINE_KEEP_NVRAM)
        self.pool.refresh(0)
        for name in self.pool.listVolumes():
            self.pool.storageVolLookupByName(name).delete(0)
        self.pool.destroy()

    def test_real_import_and_collision_refusal(self):
        items = m.prepare(self.conn, self.args)
        xml = m.domain_xml(self.args, items)
        self.conn.domainXMLToNative('qemu-argv', xml, 0)
        m.migrate(self.conn, self.args, items, xml)
        domain = self.conn.lookupByName(self.name)
        self.assertFalse(domain.isActive())
        records = m.json.loads((self.args.output_dir / 'import.json').read_text())
        self.assertEqual(len(records), 4)
        for item, record in zip(items, records):
            volume = self.pool.storageVolLookupByName(item['name'])
            info = ET.fromstring(volume.XMLDesc(0))
            expected = 'qcow2' if item['role'] in ('disk', 'opencore') else 'raw'
            self.assertEqual(info.find('./target/format').get('type'), expected)
            expected_mode = 0o644 if item['role'] == 'code' else 0o600
            self.assertEqual(int(info.findtext('./target/permissions/mode'), 8), expected_mode)
            self.assertEqual(record['sha256'], hashlib.sha256(self.originals[item['source']]).hexdigest())
            self.assertEqual(item['source'].read_bytes(), self.originals[item['source']])
        with self.assertRaisesRegex(ValueError, 'Domain already exists'):
            m.prepare(self.conn, self.args)

    def test_real_rollback_after_partial_import(self):
        items = m.prepare(self.conn, self.args)
        xml = m.domain_xml(self.args, items)
        original_upload = m.upload_verify
        def fail_second(conn, volume, item):
            if item['role'] == 'opencore':
                raise RuntimeError('injected interruption after first verified volume')
            return original_upload(conn, volume, item)
        with patch.object(m, 'upload_verify', side_effect=fail_second):
            with self.assertRaisesRegex(RuntimeError, 'injected interruption'):
                m.migrate(self.conn, self.args, items, xml)
        self.pool.refresh(0)
        self.assertEqual(self.pool.listVolumes(), [])
        self.assertFalse(any(d.name() == self.name for d in self.conn.listAllDomains(0)))
        for source, content in self.originals.items():
            self.assertEqual(source.read_bytes(), content)

    def test_real_external_data_file_rejected(self):
        path = self.root / 'external.qcow2'
        subprocess.run(['qemu-img', 'create', '-f', 'qcow2', '-o',
                        f'data_file={self.root / "external.raw"},data_file_raw=on', str(path), '8M'],
                       check=True, capture_output=True)
        with self.assertRaisesRegex(ValueError, 'External QCOW2 data files'):
            m.image_info(path)

    def test_uncached_destination_file_preserved(self):
        path = Path(ET.fromstring(self.pool.XMLDesc(0)).findtext('./target/path')) / (self.name + '.qcow2')
        path.write_bytes(b'pre-existing file outside libvirt cache')
        self.assertNotIn(path.name, self.pool.listVolumes())
        with self.assertRaisesRegex(ValueError, 'Volume already exists'):
            m.prepare(self.conn, self.args)
        self.assertEqual(path.read_bytes(), b'pre-existing file outside libvirt cache')

    def test_duplicate_and_empty_sources_rejected(self):
        self.args.firmware_vars = self.args.firmware_code
        with self.assertRaisesRegex(ValueError, 'distinct source'):
            m.prepare(self.conn, self.args)
        self.args.firmware_code.write_bytes(b'')
        with self.assertRaisesRegex(ValueError, 'Empty source'):
            m.prepare(self.conn, self.args)

    def test_insufficient_space_rejected_without_creating_volumes(self):
        with patch.object(m.shutil, 'disk_usage', return_value=shutil._ntuple_diskusage(100, 100, 0)):
            with self.assertRaisesRegex(ValueError, 'Insufficient free space'):
                m.prepare(self.conn, self.args)
        self.assertEqual(self.pool.listVolumes(), [])

    @unittest.skipUnless(shutil.which('qemu-storage-daemon'), 'qemu-storage-daemon unavailable')
    def test_active_image_writer_rejected(self):
        pidfile = self.root / 'writer.pid'
        config = m.json.dumps({'driver': 'qcow2', 'node-name': 'locked-disk',
                               'file': {'driver': 'file', 'filename': str(self.args.disk)}})
        writer = subprocess.Popen(['qemu-storage-daemon', '--blockdev', config,
                                   '--pidfile', str(pidfile)],
                                  stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        try:
            deadline = time.monotonic() + 5
            while not pidfile.exists() and writer.poll() is None and time.monotonic() < deadline:
                time.sleep(0.01)
            self.assertTrue(pidfile.exists(), 'test image writer failed to start')
            with self.assertRaisesRegex(ValueError, 'lock'):
                m.prepare(self.conn, self.args)
            self.assertEqual(self.pool.listVolumes(), [])
        finally:
            writer.terminate()
            try:
                writer.communicate(timeout=5)
            except subprocess.TimeoutExpired:
                writer.kill()
                writer.communicate(timeout=5)

    def test_lost_registration_response_keeps_real_domain_and_volumes(self):
        items = m.prepare(self.conn, self.args)
        xml = m.domain_xml(self.args, items)
        proxy = MagicMock(wraps=self.conn)
        def register_then_lose_response(config):
            self.conn.defineXML(config)
            raise RuntimeError('simulated lost registration response')
        proxy.defineXML.side_effect = register_then_lose_response
        with self.assertRaisesRegex(RuntimeError, 'lost registration response'):
            m.migrate(proxy, self.args, items, xml)
        self.assertFalse(self.conn.lookupByName(self.name).isActive())
        self.assertEqual(len(self.pool.listVolumes()), 4)
        for source, content in self.originals.items():
            self.assertEqual(source.read_bytes(), content)

    def test_shared_filesystem_space_is_summed(self):
        sizes = sum(path.stat().st_size for path in self.originals)
        available = 64 * 1024 * 1024 + sizes - 1
        usage = shutil._ntuple_diskusage(available, 0, available)
        with patch.object(m.shutil, 'disk_usage', return_value=usage):
            with self.assertRaisesRegex(ValueError, 'Insufficient free space'):
                m.prepare(self.conn, self.args)
        self.assertEqual(self.pool.listVolumes(), [])
