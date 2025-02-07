#!/usr/bin/env python3
# pylint: disable=C0301,C0116,C0103,R0903

"""
Gather recovery information for Macs.

Copyright (c) 2019, vit9696

macrecovery is a tool that helps to automate recovery interaction. It can be
used to download diagnostics and recovery as well as analyse MLB.

Requires python to run. Run with `-h` argument to see all available arguments.

Upstream: https://github.com/acidanthera/OpenCorePkg/tree/master/Utilities/macrecovery
pylint -> Your code has been rated at -0.08/10 ;(
"""

import argparse
import hashlib
import json
import linecache
import os
import random
import struct
import string
import sys

try:
    from urllib.request import Request, HTTPError, urlopen
    from urllib.parse import urlparse
except ImportError:
    print('ERROR: Python 2 is not supported, please use Python 3')
    sys.exit(1)

SELF_DIR = os.path.dirname(os.path.realpath(__file__))

# MacPro7,1
RECENT_MAC = 'Mac-27AD2F918AE68F61'
MLB_ZERO = '00000000000000000'
MLB_VALID = 'F5K105303J9K3F71M'
MLB_PRODUCT = 'F5K00000000K3F700'

TYPE_SID = 16
TYPE_K = 64
TYPE_FG = 64

INFO_PRODUCT = 'AP'
INFO_IMAGE_LINK = 'AU'
INFO_IMAGE_HASH = 'AH'
INFO_IMAGE_SESS = 'AT'
INFO_SIGN_LINK = 'CU'
INFO_SIGN_HASH = 'CH'
INFO_SIGN_SESS = 'CT'
INFO_REQURED = [INFO_PRODUCT, INFO_IMAGE_LINK, INFO_IMAGE_HASH, INFO_IMAGE_SESS, INFO_SIGN_LINK, INFO_SIGN_HASH, INFO_SIGN_SESS]

# Use -2 for better resize stability on Windows
TERMINAL_MARGIN = 2

def run_query(url, headers, post=None, raw=False):
    if post is not None:
        data = '\n'.join(entry + '=' + post[entry] for entry in post).encode()
    else:
        data = None
    req = Request(url=url, headers=headers, data=data)
    try:
        response = urlopen(req)
        if raw:
            return response
        return dict(response.info()), response.read()
    except HTTPError as e:
        print(f'ERROR: "{e}" when connecting to {url}')
        sys.exit(1)


def generate_id(id_type, id_value=None):
    return id_value or ''.join(random.choices(string.hexdigits[:16].upper(), k=id_type))


def product_mlb(mlb):
    return '00000000000' + mlb[11:15] + '00'


def mlb_from_eeee(eeee):
    if len(eeee) != 4:
        print('ERROR: Invalid EEEE code length!')
        sys.exit(1)

    return f'00000000000{eeee}00'


# zhangyoufu https://gist.github.com/MCJack123/943eaca762730ca4b7ae460b731b68e7#gistcomment-3061078 2021-10-08
Apple_EFI_ROM_public_key_1 = 0xC3E748CAD9CD384329E10E25A91E43E1A762FF529ADE578C935BDDF9B13F2179D4855E6FC89E9E29CA12517D17DFA1EDCE0BEBF0EA7B461FFE61D94E2BDF72C196F89ACD3536B644064014DAE25A15DB6BB0852ECBD120916318D1CCDEA3C84C92ED743FC176D0BACA920D3FCF3158AFF731F88CE0623182A8ED67E650515F75745909F07D415F55FC15A35654D118C55A462D37A3ACDA08612F3F3F6571761EFCCBCC299AEE99B3A4FD6212CCFFF5EF37A2C334E871191F7E1C31960E010A54E86FA3F62E6D6905E1CD57732410A3EB0C6B4DEFDABE9F59BF1618758C751CD56CEF851D1C0EAA1C558E37AC108DA9089863D20E2E7E4BF475EC66FE6B3EFDCF

ChunkListHeader = struct.Struct('<4sIBBBxQQQ')
assert ChunkListHeader.size == 0x24

Chunk = struct.Struct('<I32s')
assert Chunk.size == 0x24


def verify_chunklist(cnkpath):
    with open(cnkpath, 'rb') as f:
        hash_ctx = hashlib.sha256()
        data = f.read(ChunkListHeader.size)
        hash_ctx.update(data)
        magic, header_size, file_version, chunk_method, signature_method, chunk_count, chunk_offset, signature_offset = ChunkListHeader.unpack(data)
        assert magic == b'CNKL'
        assert header_size == ChunkListHeader.size
        assert file_version == 1
        assert chunk_method == 1
        assert signature_method in [1, 2]
        assert chunk_count > 0
        assert chunk_offset == 0x24
        assert signature_offset == chunk_offset + Chunk.size * chunk_count
        for _ in range(chunk_count):
            data = f.read(Chunk.size)
            hash_ctx.update(data)
            chunk_size, chunk_sha256 = Chunk.unpack(data)
            yield chunk_size, chunk_sha256
        digest = hash_ctx.digest()
        if signature_method == 1:
            data = f.read(256)
            assert len(data) == 256
            signature = int.from_bytes(data, 'little')
            plaintext = int(f'0x1{"f"*404}003031300d060960864801650304020105000420{"0"*64}', 16) | int.from_bytes(digest, 'big')
            assert pow(signature, 0x10001, Apple_EFI_ROM_public_key_1) == plaintext
        elif signature_method == 2:
            data = f.read(32)
            assert data == digest
            raise RuntimeError('Chunklist missing digital signature')
        else:
            raise NotImplementedError
        assert f.read(1) == b''


def get_session(args):
    headers = {
        'Host': 'osrecovery.apple.com',
        'Connection': 'close',
        'User-Agent': 'InternetRecovery/1.0',
    }

    headers, _ = run_query('http://osrecovery.apple.com/', headers)

    if args.verbose:
        print('Session headers:')
        for header in headers:
            print(f'{header}: {headers[header]}')

    for header in headers:
        if header.lower() == 'set-cookie':
            cookies = headers[header].split('; ')
            for cookie in cookies:
                return cookie if cookie.startswith('session=') else ...

    raise RuntimeError('No session in headers ' + str(headers))


def get_image_info(session, bid, mlb=MLB_ZERO, diag=False, os_type='default', cid=None):
    headers = {
        'Host': 'osrecovery.apple.com',
        'Connection': 'close',
        'User-Agent': 'InternetRecovery/1.0',
        'Cookie': session,
        'Content-Type': 'text/plain',
    }

    post = {
        'cid': generate_id(TYPE_SID, cid),
        'sn': mlb,
        'bid': bid,
        'k': generate_id(TYPE_K),
        'fg': generate_id(TYPE_FG)
    }

    if diag:
        url = 'http://osrecovery.apple.com/InstallationPayload/Diagnostics'
    else:
        url = 'http://osrecovery.apple.com/InstallationPayload/RecoveryImage'
        post['os'] = os_type

    headers, output = run_query(url, headers, post)

    output = output.decode('utf-8')
    info = {}
    for line in output.split('\n'):
        try:
            key, value = line.split(': ')
            info[key] = value
        except KeyError:
            continue
        except ValueError:
            continue

    for k in INFO_REQURED:
        if k not in info:
            raise RuntimeError(f'Missing key {k}')

    return info


def save_image(url, sess, filename='', directory=''):
    purl = urlparse(url)
    headers = {
        'Host': purl.hostname,
        'Connection': 'close',
        'User-Agent': 'InternetRecovery/1.0',
        'Cookie': '='.join(['AssetToken', sess])
    }

    if not os.path.exists(directory):
        os.makedirs(directory)

    if filename == '':
        filename = os.path.basename(purl.path)
    if filename.find(os.sep) >= 0 or filename == '':
        raise RuntimeError('Invalid save path ' + filename)

    print(f'Saving {url} to {directory}{os.sep}{filename}...')

    with open(os.path.join(directory, filename), 'wb') as fh:
        response = run_query(url, headers, raw=True)
        headers = dict(response.headers)
        totalsize = -1
        for header in headers:
            if header.lower() == 'content-length':
                totalsize = int(headers[header])
                break
        size = 0
        oldterminalsize = 0
        while True:
            chunk = response.read(2**20)
            if not chunk:
                break
            fh.write(chunk)
            size += len(chunk)
            try:
                terminalsize = max(os.get_terminal_size().columns - TERMINAL_MARGIN, 0)
            except OSError:
                terminalsize = 80
            if oldterminalsize != terminalsize:
                print(f'\r{"":<{terminalsize}}', end='')
                oldterminalsize = terminalsize
            if totalsize > 0:
                progress = size / totalsize
                barwidth = terminalsize // 3
                print(f'\r{size / (2**20):.1f}/{totalsize / (2**20):.1f} MB ', end='')
                if terminalsize > 55:
                    print(f'|{"=" * int(barwidth * progress):<{barwidth}}|', end='')
                print(f' {progress*100:.1f}% downloaded', end='')
            else:
                # Fallback if Content-Length isn't available
                print(f'\r{size / (2**20)} MB downloaded...', end='')
            sys.stdout.flush()
        print('\nDownload complete!')

    return os.path.join(directory, os.path.basename(filename))


def verify_image(dmgpath, cnkpath):
    print('Verifying image with chunklist...')

    with open(dmgpath, 'rb') as dmgf:
        for cnkcount, (cnksize, cnkhash) in enumerate(verify_chunklist(cnkpath), 1):
            terminalsize = max(os.get_terminal_size().columns - TERMINAL_MARGIN, 0)
            print(f'\r{f"Chunk {cnkcount} ({cnksize} bytes)":<{terminalsize}}', end='')
            sys.stdout.flush()
            cnk = dmgf.read(cnksize)
            if len(cnk) != cnksize:
                raise RuntimeError(f'Invalid chunk {cnkcount} size: expected {cnksize}, read {len(cnk)}')
            if hashlib.sha256(cnk).digest() != cnkhash:
                raise RuntimeError(f'Invalid chunk {cnkcount}: hash mismatch')
        if dmgf.read(1) != b'':
            raise RuntimeError('Invalid image: larger than chunklist')
        print('\nImage verification complete!')


def action_download(args):
    """
    Reference information for queries:

    Recovery latest:
    cid=3076CE439155BA14
    sn=...
    bid=Mac-E43C1C25D4880AD6
    k=4BE523BB136EB12B1758C70DB43BDD485EBCB6A457854245F9E9FF0587FB790C
    os=latest
    fg=B2E6AA07DB9088BE5BDB38DB2EA824FDDFB6C3AC5272203B32D89F9D8E3528DC

    Recovery default:
    cid=4A35CB95FF396EE7
    sn=...
    bid=Mac-E43C1C25D4880AD6
    k=0A385E6FFC3DDD990A8A1F4EC8B98C92CA5E19C9FF1DD26508C54936D8523121
    os=default
    fg=B2E6AA07DB9088BE5BDB38DB2EA824FDDFB6C3AC5272203B32D89F9D8E3528DC

    Diagnostics:
    cid=050C59B51497CEC8
    sn=...
    bid=Mac-E43C1C25D4880AD6
    k=37D42A8282FE04A12A7D946304F403E56A2155B9622B385F3EB959A2FBAB8C93
    fg=B2E6AA07DB9088BE5BDB38DB2EA824FDDFB6C3AC5272203B32D89F9D8E3528DC
    """

    session = get_session(args)
    info = get_image_info(session, bid=args.board_id, mlb=args.mlb, diag=args.diagnostics, os_type=args.os_type)
    if args.verbose:
        print(info)
    print(f'Downloading {info[INFO_PRODUCT]}...')
    cnkname = '' if args.basename == '' else args.basename + '.chunklist'
    cnkpath = save_image(info[INFO_SIGN_LINK], info[INFO_SIGN_SESS], cnkname, args.outdir)
    dmgname = '' if args.basename == '' else args.basename + '.dmg'
    dmgpath = save_image(info[INFO_IMAGE_LINK], info[INFO_IMAGE_SESS], dmgname, args.outdir)
    try:
        verify_image(dmgpath, cnkpath)
        return 0
    except Exception as err:
        if isinstance(err, AssertionError) and str(err) == '':
            try:
                tb = sys.exc_info()[2]
                while tb.tb_next:
                    tb = tb.tb_next
                err = linecache.getline(tb.tb_frame.f_code.co_filename, tb.tb_lineno, tb.tb_frame.f_globals).strip()
            except Exception:
                err = "Invalid chunklist"
        print(f'\rImage verification failed. ({err})')
        return 1


def action_selfcheck(args):
    """
    Sanity check server logic for recovery:

    if not valid(bid):
        return error()
    ppp = get_ppp(sn)
    if not valid(ppp):
        return latest_recovery(bid = bid)             # Returns newest for bid.
    if valid(sn):
        if os == 'default':
            return default_recovery(sn = sn, ppp = ppp) # Returns oldest for sn.
        else:
            return latest_recovery(sn = sn, ppp = ppp)  # Returns newest for sn.
    return default_recovery(ppp = ppp)              # Returns oldest.
    """

    session = get_session(args)
    valid_default = get_image_info(session, bid=RECENT_MAC, mlb=MLB_VALID, diag=False, os_type='default')
    valid_latest = get_image_info(session, bid=RECENT_MAC, mlb=MLB_VALID, diag=False, os_type='latest')
    product_default = get_image_info(session, bid=RECENT_MAC, mlb=MLB_PRODUCT, diag=False, os_type='default')
    product_latest = get_image_info(session, bid=RECENT_MAC, mlb=MLB_PRODUCT, diag=False, os_type='latest')
    generic_default = get_image_info(session, bid=RECENT_MAC, mlb=MLB_ZERO, diag=False, os_type='default')
    generic_latest = get_image_info(session, bid=RECENT_MAC, mlb=MLB_ZERO, diag=False, os_type='latest')

    if args.verbose:
        print(valid_default)
        print(valid_latest)
        print(product_default)
        print(product_latest)
        print(generic_default)
        print(generic_latest)

    if valid_default[INFO_PRODUCT] == valid_latest[INFO_PRODUCT]:
        # Valid MLB must give different default and latest if this is not a too new product.
        print(f'ERROR: Cannot determine any previous product, got {valid_default[INFO_PRODUCT]}')
        return 1

    if product_default[INFO_PRODUCT] != product_latest[INFO_PRODUCT]:
        # Product-only MLB must give the same value for default and latest.
        print(f'ERROR: Latest and default do not match for product MLB, got {product_default[INFO_PRODUCT]} and {product_latest[INFO_PRODUCT]}')
        return 1

    if generic_default[INFO_PRODUCT] != generic_latest[INFO_PRODUCT]:
        # Zero MLB always give the same value for default and latest.
        print(f'ERROR: Generic MLB gives different product, got {generic_default[INFO_PRODUCT]} and {generic_latest[INFO_PRODUCT]}')
        return 1

    if valid_latest[INFO_PRODUCT] != generic_latest[INFO_PRODUCT]:
        # Valid MLB must always equal generic MLB.
        print(f'ERROR: Cannot determine unified latest product, got {valid_latest[INFO_PRODUCT]} and {generic_latest[INFO_PRODUCT]}')
        return 1

    if product_default[INFO_PRODUCT] != valid_default[INFO_PRODUCT]:
        # Product-only MLB can give the same value with valid default MLB.
        # This is not an error for all models, but for our chosen code it is.
        print(f'ERROR: Valid and product MLB give mismatch, got {product_default[INFO_PRODUCT]} and {valid_default[INFO_PRODUCT]}')
        return 1

    print('SUCCESS: Found no discrepancies with MLB validation algorithm!')
    return 0


def action_verify(args):
    """
    Try to verify MLB serial number.
    """
    session = get_session(args)
    generic_latest = get_image_info(session, bid=RECENT_MAC, mlb=MLB_ZERO, diag=False, os_type='latest')
    uvalid_default = get_image_info(session, bid=args.board_id, mlb=args.mlb, diag=False, os_type='default')
    uvalid_latest = get_image_info(session, bid=args.board_id, mlb=args.mlb, diag=False, os_type='latest')
    uproduct_default = get_image_info(session, bid=args.board_id, mlb=product_mlb(args.mlb), diag=False, os_type='default')

    if args.verbose:
        print(generic_latest)
        print(uvalid_default)
        print(uvalid_latest)
        print(uproduct_default)

    # Verify our MLB number.
    if uvalid_default[INFO_PRODUCT] != uvalid_latest[INFO_PRODUCT]:
        print(f'SUCCESS: {args.mlb} MLB looks valid and supported!' if uvalid_latest[INFO_PRODUCT] == generic_latest[INFO_PRODUCT] else f'SUCCESS: {args.mlb} MLB looks valid, but probably unsupported!')
        return 0

    print('UNKNOWN: Run selfcheck, check your board-id, or try again later!')

    # Here we have matching default and latest products. This can only be true for very
    # new models. These models get either latest or special builds.
    if uvalid_default[INFO_PRODUCT] == generic_latest[INFO_PRODUCT]:
        print(f'UNKNOWN: {args.mlb} MLB can be valid if very new!')
        return 0
    if uproduct_default[INFO_PRODUCT] != uvalid_default[INFO_PRODUCT]:
        print(f'UNKNOWN: {args.mlb} MLB looks invalid, other models use product {uproduct_default[INFO_PRODUCT]} instead of {uvalid_default[INFO_PRODUCT]}!')
        return 0
    print(f'UNKNOWN: {args.mlb} MLB can be valid if very new and using special builds!')
    return 0


def action_guess(args):
    """
    Attempt to guess which model does this MLB belong.
    """

    mlb = args.mlb
    anon = mlb.startswith('000')

    with open(args.board_db, 'r', encoding='utf-8') as fh:
        db = json.load(fh)

    supported = {}

    session = get_session(args)

    generic_latest = get_image_info(session, bid=RECENT_MAC, mlb=MLB_ZERO, diag=False, os_type='latest')

    for model in db:
        try:
            if anon:
                # For anonymous lookup check when given model does not match latest.
                model_latest = get_image_info(session, bid=model, mlb=MLB_ZERO, diag=False, os_type='latest')

                if model_latest[INFO_PRODUCT] != generic_latest[INFO_PRODUCT]:
                    if db[model] == 'current':
                        print(f'WARN: Skipped {model} due to using latest product {model_latest[INFO_PRODUCT]} instead of {generic_latest[INFO_PRODUCT]}')
                    continue

                user_default = get_image_info(session, bid=model, mlb=mlb, diag=False, os_type='default')

                if user_default[INFO_PRODUCT] != generic_latest[INFO_PRODUCT]:
                    supported[model] = [db[model], user_default[INFO_PRODUCT], generic_latest[INFO_PRODUCT]]
            else:
                # For normal lookup check when given model has mismatching normal and latest.
                user_latest = get_image_info(session, bid=model, mlb=mlb, diag=False, os_type='latest')

                user_default = get_image_info(session, bid=model, mlb=mlb, diag=False, os_type='default')

                if user_latest[INFO_PRODUCT] != user_default[INFO_PRODUCT]:
                    supported[model] = [db[model], user_default[INFO_PRODUCT], user_latest[INFO_PRODUCT]]

        except Exception as e:
            print(f'WARN: Failed to check {model}, exception: {e}')

    if len(supported) > 0:
        print(f'SUCCESS: MLB {mlb} looks supported for:')
        for model in supported.items():
            print(f'- {model}, up to {supported[model][0]}, default: {supported[model][1]}, latest: {supported[model][2]}')
        return 0

    print(f'UNKNOWN: Failed to determine supported models for MLB {mlb}!')
    return None


# https://stackoverflow.com/questions/2280334/shortest-way-of-creating-an-object-with-arbitrary-attributes-in-python
class gdata:
    """
    A string to make pylint happy ;)
    """
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)

def main():
    parser = argparse.ArgumentParser(description='Gather recovery information for Macs')
    parser.add_argument('--action', choices=['download', 'selfcheck', 'verify', 'guess'], default='',
                        help='Action to perform: "download" - performs recovery downloading,'
                        ' "selfcheck" checks whether MLB serial validation is possible, "verify" performs'
                        ' MLB serial verification, "guess" tries to find suitable mac model for MLB.')
    parser.add_argument('-o', '--outdir', type=str, default='com.apple.recovery.boot',
                        help='customise output directory for downloading, defaults to com.apple.recovery.boot')
    parser.add_argument('-n', '--basename', type=str, default='',
                        help='customise base name for downloading, defaults to remote name')
    parser.add_argument('-b', '--board-id', type=str, default=RECENT_MAC,
                        help=f'use specified board identifier for downloading, defaults to {RECENT_MAC}')
    parser.add_argument('-m', '--mlb', type=str, default=MLB_ZERO,
                        help=f'use specified logic board serial for downloading, defaults to {MLB_ZERO}')
    parser.add_argument('-e', '--code', type=str, default='',
                        help='generate product logic board serial with specified product EEEE code')
    parser.add_argument('-os', '--os-type', type=str, default='default', choices=['default', 'latest'],
                        help=f'use specified os type, defaults to default {MLB_ZERO}')
    parser.add_argument('-diag', '--diagnostics', action='store_true', help='download diagnostics image')
    parser.add_argument('-s', '--shortname', type=str, default='',
                        help='available options: high-sierra, mojave, catalina, big-sur, monterey, ventura, sonoma, sequoia')
    parser.add_argument('-v', '--verbose', action='store_true', help='print debug information')
    parser.add_argument('-db', '--board-db', type=str, default=os.path.join(SELF_DIR, 'boards.json'),
                        help='use custom board list for checking, defaults to boards.json')

    args = parser.parse_args()

    if args.code != '':
        args.mlb = mlb_from_eeee(args.code)

    if len(args.mlb) != 17:
        print('ERROR: Cannot use MLBs in non 17 character format!')
        sys.exit(1)

    if args.action == 'download':
        return action_download(args)
    if args.action == 'selfcheck':
        return action_selfcheck(args)
    if args.action == 'verify':
        return action_verify(args)
    if args.action == 'guess':
        return action_guess(args)

    # No action specified, so present a download menu instead
    # https://github.com/acidanthera/OpenCorePkg/blob/master/Utilities/macrecovery/boards.json
    # https://github.com/corpnewt/gibMacOS
    products = [
            {"name": "High Sierra (10.13)", "b": "Mac-7BA5B2D9E42DDD94", "m": "00000000000J80300", "short": "high-sierra"},
            {"name": "Mojave (10.14)", "b": "Mac-7BA5B2DFE22DDD8C", "m": "00000000000KXPG00", "short": "mojave"},
            {"name": "Catalina (10.15)", "b": "Mac-00BE6ED71E35EB86", "m": "00000000000000000", "short": "catalina"},
            {"name": "Big Sur (11.7)", "b": "Mac-2BD1B31983FE1663", "m": "00000000000000000", "short": "big-sur"},
            {"name": "Monterey (12.6)", "b": "Mac-B809C3757DA9BB8D", "m": "00000000000000000", "os_type": "latest", "short": "monterey"},
            {"name": "Ventura (13)", "b": "Mac-4B682C642B45593E", "m": "00000000000000000", "os_type": "latest", "short": "ventura"},
            {"name": "Sonoma (14)  - RECOMMENDED", "b": "Mac-827FAC58A8FDFA22", "m": "00000000000000000", "short": "sonoma"},
            {"name": "Sequoia (15) ", "b": "Mac-7BA5B2D9E42DDD94", "m": "00000000000000000", "short": "sequoia", "os_type": "latest"},
    ]
    for index, product in enumerate(products):
        name = product["name"]
        print('%s. %12s' % (index + 1, name))
    # test locally using args.shortname = 'mojave'
    if not args.shortname or args.shortname == '':
        answer = input('\nChoose a product to download (1-%s): ' % len(products))
        try:
            index = int(answer) - 1
            if index < 0:
                raise ValueError
        except (ValueError, IndexError):
            pass
    else:
        index = 0
        for product in products:
            if args.shortname == product['short']:
                break
            else:
                index = index+1
    product = products[index]
    try:
        os_type = product["os_type"]
    except:
        os_type = "default"
    args = gdata(mlb = product["m"], board_id = product["b"], diagnostics =
            False, os_type = os_type, verbose=False, basename="", outdir=".")
    action_download(args)


if __name__ == '__main__':
    sys.exit(main())
