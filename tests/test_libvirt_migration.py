"""Failure handling and generated hardware contract for the migration helper."""
import importlib.util
import io
from pathlib import Path
import tempfile
import unittest
from unittest.mock import MagicMock, patch
import xml.etree.ElementTree as ET

SPEC = importlib.util.spec_from_file_location('migration', Path(__file__).resolve().parents[1] / 'migrate-to-libvirt.py')
m = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(m)


class MigrationTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.directory = Path(self.temp.name)
        self.original_image_info = m.image_info
        lock_check = patch.object(m, 'image_info', return_value={'format': 'raw'})
        self.image_info_mock = lock_check.start()
        self.addCleanup(lock_check.stop)
        self.args = m.parser().parse_args(['--name', 'test-mac', '--output-dir', str(self.directory / 'output')])
        m.validate_args(self.args)
        self.items = []
        for role in ('disk', 'opencore', 'code', 'vars'):
            source = self.directory / role
            source.write_bytes(b'original-content')
            self.items.append(dict(role=role, source=source, name=role,
                                   path=self.directory / ('dest & ' + role),
                                   pool=MagicMock(), before=m.fingerprint(source)))

    def test_xml_preserves_working_hardware_and_escapes_paths(self):
        root = ET.fromstring(m.domain_xml(self.args, self.items))
        self.assertEqual(root.find('./devices/disk/source').get('file'), str(self.items[1]['path']))
        usb = root.find("./devices/controller[@type='usb']/address")
        self.assertEqual((usb.get('bus'), usb.get('slot')), ('0x00', '0x02'))
        self.assertEqual(root.find('./devices/graphics/mouse').get('mode'), 'client')
        self.assertEqual(len(root.findall('./devices/disk')), 2)
        self.assertEqual(root.find('vcpu').text, '4')
        args = [n.get('value') for n in root.findall(f'./{{{m.NS}}}commandline/{{{m.NS}}}arg')]
        self.assertIn(self.args.cpu_model + ',' + m.CPU_FLAGS, args)
        self.assertTrue(any('addr=0x5' in value for value in args))

    def test_unique_identity(self):
        first = m.domain_xml(self.args, self.items)
        second = m.domain_xml(self.args, self.items)
        self.assertNotEqual(ET.fromstring(first).findtext('uuid'), ET.fromstring(second).findtext('uuid'))

    def test_invalid_values_and_output_collision(self):
        for option, value in [('--name', '../mac'), ('--cpu-model', 'host,+extra'), ('--ram', '0'), ('--ssh-port', '22')]:
            with self.subTest(option=option), self.assertRaises(ValueError):
                m.validate_args(m.parser().parse_args([option, value]))
        self.args.output_dir.mkdir()
        with self.assertRaises(ValueError):
            m.validate_args(self.args)

    def test_existing_domain_rejected_before_creating_storage(self):
        conn = MagicMock()
        conn.listAllDomains.return_value = [MagicMock()]
        conn.listAllDomains.return_value[0].name.return_value = self.args.name
        with self.assertRaises(ValueError):
            m.prepare(conn, self.args)
        conn.storagePoolLookupByName.assert_not_called()

    def test_existing_volume_rejected(self):
        conn = MagicMock()
        conn.listAllDomains.return_value = []
        pool = MagicMock()
        pool.listVolumes.return_value = [self.args.name + '.qcow2']
        with patch.object(m, 'pool_details', return_value=(pool, self.directory)):
            with self.assertRaisesRegex(ValueError, 'Volume already exists'):
                m.prepare(conn, self.args)
        pool.createXML.assert_not_called()

    def test_upload_failure_aborts_stream(self):
        conn = MagicMock()
        stream = conn.newStream.return_value
        stream.send.side_effect = RuntimeError('disconnected')
        with self.assertRaisesRegex(RuntimeError, 'disconnected'):
            m.upload_verify(conn, MagicMock(), self.items[0])
        stream.abort.assert_called_once()

    def test_dry_run_does_not_import_or_create_output(self):
        fake_libvirt = MagicMock()
        with patch.object(m.sys, 'argv', ['helper', '--name', 'dry-test', '--dry-run',
                                        '--output-dir', str(self.args.output_dir)]), \
             patch.dict(m.sys.modules, {'libvirt': fake_libvirt}), \
             patch.object(m.shutil, 'which', return_value='/usr/bin/qemu-img'), \
             patch.object(m, 'prepare', return_value=self.items), \
             patch.object(m, 'migrate') as migrate, \
             patch('sys.stdout', new_callable=io.StringIO):
            self.assertEqual(m.main(), 0)
        migrate.assert_not_called()
        self.assertFalse(self.args.output_dir.exists())

    def test_backing_chain_rejected(self):
        result = MagicMock(stdout='{"format":"qcow2","backing-filename":"base.qcow2"}')
        with patch.object(m.subprocess, 'run', return_value=result), self.assertRaises(ValueError):
            self.original_image_info(self.items[0]['source'])

    def test_checksum_mismatch_aborts_registration(self):
        conn = MagicMock()
        upload = MagicMock()
        upload.send.side_effect = lambda chunk: len(chunk)
        download = MagicMock()
        download.recv.side_effect = [b'wrong bytes', b'']
        conn.newStream.side_effect = [upload, download]
        with self.assertRaisesRegex(RuntimeError, 'Checksum mismatch'):
            m.upload_verify(conn, MagicMock(), self.items[0])

    def test_partial_sends_supported(self):
        conn = MagicMock()
        upload = MagicMock()
        upload.send.side_effect = lambda chunk: min(3, len(chunk))
        download = MagicMock()
        download.recv.side_effect = [b'original-content', b'']
        conn.newStream.side_effect = [upload, download]
        self.assertEqual(m.upload_verify(conn, MagicMock(), self.items[0]), m.hashlib.sha256(b'original-content').hexdigest())
        self.assertGreater(upload.send.call_count, 1)

    def test_failed_transfer_deletes_only_new_volume(self):
        conn = MagicMock()
        volume = self.items[0]['pool'].createXML.return_value
        with patch.object(m, 'upload_verify', side_effect=RuntimeError('transfer failed')):
            with self.assertRaisesRegex(RuntimeError, 'transfer failed'):
                m.migrate(conn, self.args, self.items, '<domain/>')
        volume.delete.assert_called_once_with(0)
        conn.defineXML.assert_not_called()
        self.assertTrue(self.items[0]['source'].exists())
        self.items[1]['pool'].createXML.assert_not_called()

    def test_start_failure_retains_registered_vm_storage(self):
        conn = MagicMock()
        domain = conn.defineXML.return_value
        domain.XMLDesc.return_value = '<domain/>'
        domain.create.side_effect = RuntimeError('start failed')
        self.args.start = True
        with patch.object(m, 'upload_verify', return_value='checksum'):
            with self.assertRaisesRegex(RuntimeError, 'start failed'):
                m.migrate(conn, self.args, self.items, '<domain/>')
        for item in self.items:
            item['pool'].createXML.return_value.delete.assert_not_called()

    def test_source_changed_before_upload(self):
        self.items[0]['source'].write_bytes(b'changed')
        with self.assertRaisesRegex(RuntimeError, 'Source changed'):
            m.migrate(MagicMock(), self.args, self.items, '<domain/>')
        self.items[0]['pool'].createXML.assert_not_called()


if __name__ == '__main__':
    unittest.main()
