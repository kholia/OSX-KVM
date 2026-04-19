#!/usr/bin/env python3

import argparse
import hashlib
import json
import os
import random
import string
import struct
import sys
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Iterator
from urllib.request import Request, urlopen
from urllib.parse import urlparse
from urllib.error import HTTPError

SELF_DIR = Path(__file__).parent.resolve()
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

TERMINAL_MARGIN = 2

Apple_EFI_ROM_public_key_1 = 0xC3E748CAD9CD384329E10E25A91E43E1A762FF529ADE578C935BDDF9B13F2179D4855E6FC89E9E29CA12517D17DFA1EDCE0BEBF0EA7B461FFE61D94E2BDF72C196F89ACD3536B644064014DAE25A15DB6BB0852ECBD120916318D1CCDEA3C84C92ED743FC176D0BACA920D3FCF3158AFF731F88CE0623182A8ED67E650515F75745909F07D415F55FC15A35654D118C55A462D37A3ACDA08612F3F3F6571761EFCCBCC299AEE99B3A4FD6212CCFFF5EF37A2C334E871191F7E1C31960E010A54E86FA3F62E6D6905E1CD57732410A3EB0C6B4DEFDABE9F59BF1618758C751CD56CEF851D1C0EAA1C558E37AC108DA9089863D20E2E7E4BF475EC66FE6B3EFDCF

ChunkListHeader = struct.Struct('<4sIBBBxQQQ')
Chunk = struct.Struct('<I32s')

class MacRecoveryError(Exception):
    pass

class InvalidMLBError(MacRecoveryError):
    pass

class VerificationError(MacRecoveryError):
    pass

def generate_id(length: int, value: Optional[str] = None) -> str:
    return value or ''.join(random.choices(string.hexdigits[:16].upper(), k=length))

def product_mlb(mlb: str) -> str:
    if len(mlb) != 17:
        raise InvalidMLBError("MLB must be 17 characters")
    return '00000000000' + mlb[11:15] + '00'

def mlb_from_eeee(eeee: str) -> str:
    if len(eeee) != 4:
        raise InvalidMLBError("EEEE code must be 4 characters")
    return f'00000000000{eeee}00'

def run_query(url: str, headers: Dict[str, str], post: Optional[Dict[str, str]] = None, raw: bool = False):
    data = '\n'.join(f"{k}={v}" for k, v in (post or {}).items()).encode() if post else None
    req = Request(url=url, headers=headers, data=data)
    
    try:
        with urlopen(req) as response:
            if raw:
                return response
            return dict(response.info()), response.read()
    except HTTPError as e:
        raise MacRecoveryError(f"HTTP error {e.code}: {e.reason} for {url}") from e

def get_session(verbose: bool = False) -> str:
    headers = {
        'Host': 'osrecovery.apple.com',
        'Connection': 'close',
        'User-Agent': 'InternetRecovery/1.0',
    }
    
    headers_resp, _ = run_query('http://osrecovery.apple.com/', headers)
    
    if verbose:
        print("Session headers:")
        for k, v in headers_resp.items():
            print(f"{k}: {v}")
    
    for header, value in headers_resp.items():
        if header.lower() == 'set-cookie':
            cookies = value.split('; ')
            for cookie in cookies:
                if cookie.startswith('session='):
                    return cookie
    
    raise MacRecoveryError("No session cookie found")

def parse_image_info(output: bytes) -> Dict[str, str]:
    info = {}
    for line in output.decode('utf-8').split('\n'):
        if ': ' in line:
            key, value = line.split(': ', 1)
            info[key] = value
    
    missing = [k for k in INFO_REQURED if k not in info]
    if missing:
        raise MacRecoveryError(f"Missing required keys: {missing}")
    
    return info

def get_image_info(session: str, bid: str, mlb: str = MLB_ZERO, diag: bool = False, 
                  os_type: str = 'default', cid: Optional[str] = None) -> Dict[str, str]:
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

    url = ('http://osrecovery.apple.com/InstallationPayload/Diagnostics' 
           if diag else 'http://osrecovery.apple.com/InstallationPayload/RecoveryImage')
    if not diag:
        post['os'] = os_type

    headers_resp, output = run_query(url, headers, post)
    return parse_image_info(output)

def save_image(url: str, sess: str, filename: str = '', directory: str = '.') -> str:
    purl = urlparse(url)
    headers = {
        'Host': purl.hostname,
        'Connection': 'close',
        'User-Agent': 'InternetRecovery/1.0',
        'Cookie': f'AssetToken={sess}'
    }

    directory = Path(directory)
    directory.mkdir(parents=True, exist_ok=True)
    
    filename = filename or Path(purl.path).name
    filepath = directory / filename

    print(f"Saving {url} to {filepath}...")
    
    with urlopen(Request(url=url, headers=headers)) as response, open(filepath, 'wb') as fh:
        totalsize = int(response.headers.get('content-length', 0))
        size = 0
        
        try:
            terminalsize = max(os.get_terminal_size().columns - TERMINAL_MARGIN, 40)
        except OSError:
            terminalsize = 80

        while True:
            chunk = response.read(2**20)
            if not chunk:
                break
            fh.write(chunk)
            size += len(chunk)
            
            if totalsize:
                progress = size / totalsize
                barwidth = terminalsize // 3
                print(f"\r{size/(2**20):.1f}/{totalsize/(2**20):.1f} MB "
                      f"|{'='*int(barwidth*progress):<{barwidth}}| "
                      f"{progress*100:.1f}%", end='')
            else:
                print(f"\r{size/(2**20):.1f} MB downloaded...", end='')
            sys.stdout.flush()
    
    print(f"\nDownload complete: {filepath}")
    return str(filepath)

def verify_chunklist(cnkpath: str) -> Iterator[Tuple[int, bytes]]:
    with open(cnkpath, 'rb') as f:
        hash_ctx = hashlib.sha256()
        data = f.read(ChunkListHeader.size)
        hash_ctx.update(data)
        
        magic, header_size, file_version, chunk_method, signature_method, chunk_count, chunk_offset, signature_offset = ChunkListHeader.unpack(data)
        
        if (magic != b'CNKL' or header_size != ChunkListHeader.size or file_version != 1 or 
            chunk_method != 1 or signature_method not in (1, 2) or chunk_count <= 0 or
            chunk_offset != 0x24 or signature_offset != chunk_offset + Chunk.size * chunk_count):
            raise VerificationError("Invalid chunklist header")
        
        for i in range(chunk_count):
            data = f.read(Chunk.size)
            if len(data) != Chunk.size:
                raise VerificationError("Invalid chunk header size")
            hash_ctx.update(data)
            chunk_size, chunk_sha256 = Chunk.unpack(data)
            yield chunk_size, chunk_sha256
        
        digest = hash_ctx.digest()
        signature_data = f.read(256 if signature_method == 1 else 32)
        
        if signature_method == 1:
            if len(signature_data) != 256:
                raise VerificationError("Invalid signature size")
            signature = int.from_bytes(signature_data, 'little')
            plaintext = (int(f'0x1{"f"*404}003031300d060960864801650304020105000420{"0"*64}', 16) | 
                        int.from_bytes(digest, 'big'))
            if pow(signature, 0x10001, Apple_EFI_ROM_public_key_1) != plaintext:
                raise VerificationError("Signature verification failed")
        elif signature_method == 2:
            if signature_data != digest:
                raise VerificationError("Digest mismatch")
        else:
            raise VerificationError("Unsupported signature method")
        
        if f.read(1):
            raise VerificationError("Extra data after signature")

def verify_image(dmgpath: str, cnkpath: str):
    print("Verifying image with chunklist...")
    
    try:
        with open(dmgpath, 'rb') as dmgf:
            cnkcount = 0
            for cnkcount, (cnksize, cnkhash) in enumerate(verify_chunklist(cnkpath), 1):
                try:
                    terminalsize = max(os.get_terminal_size().columns - TERMINAL_MARGIN, 40)
                except OSError:
                    terminalsize = 80
                
                print(f"\r{'Chunk ' + str(cnkcount) + f' ({cnksize} bytes)':<{terminalsize}}", end='')
                sys.stdout.flush()
                
                cnk = dmgf.read(cnksize)
                if len(cnk) != cnksize:
                    raise VerificationError(f"Chunk {cnkcount} size mismatch: expected {cnksize}, got {len(cnk)}")
                if hashlib.sha256(cnk).digest() != cnkhash:
                    raise VerificationError(f"Chunk {cnkcount} hash mismatch")
            
            if dmgf.read(1):
                raise VerificationError("Image larger than chunklist")
        
        print("\nImage verification complete!")
    except VerificationError as e:
        raise VerificationError(f"Verification failed: {e}")

def action_download(args):
    session = get_session(args.verbose)
    info = get_image_info(session, args.board_id, args.mlb, args.diagnostics, args.os_type)
    
    if args.verbose:
        print(json.dumps(info, indent=2))
    
    print(f"Downloading {info[INFO_PRODUCT]}...")
    
    cnkname = f"{args.basename}.chunklist" if args.basename else ""
    cnkpath = save_image(info[INFO_SIGN_LINK], info[INFO_SIGN_SESS], cnkname, args.outdir)
    
    dmgname = f"{args.basename}.dmg" if args.basename else ""
    dmgpath = save_image(info[INFO_IMAGE_LINK], info[INFO_IMAGE_SESS], dmgname, args.outdir)
    
    try:
        verify_image(dmgpath, cnkpath)
        return 0
    except VerificationError as e:
        print(f"\nImage verification failed: {e}")
        return 1

def action_selfcheck(args):
    session = get_session(args.verbose)
    
    tests = [
        ('valid_default', get_image_info(session, RECENT_MAC, MLB_VALID, False, 'default')),
        ('valid_latest', get_image_info(session, RECENT_MAC, MLB_VALID, False, 'latest')),
        ('product_default', get_image_info(session, RECENT_MAC, MLB_PRODUCT, False, 'default')),
        ('product_latest', get_image_info(session, RECENT_MAC, MLB_PRODUCT, False, 'latest')),
        ('generic_default', get_image_info(session, RECENT_MAC, MLB_ZERO, False, 'default')),
        ('generic_latest', get_image_info(session, RECENT_MAC, MLB_ZERO, False, 'latest')),
    ]
    
    if args.verbose:
        for name, info in tests:
            print(f"{name}:")
            print(json.dumps(info, indent=2))
    
    valid_default, valid_latest = tests[0][1], tests[1][1]
    product_default, product_latest = tests[2][1], tests[3][1]
    generic_default, generic_latest = tests[4][1], tests[5][1]
    
    if valid_default[INFO_PRODUCT] == valid_latest[INFO_PRODUCT]:
        print(f"ERROR: Cannot determine previous product, got {valid_default[INFO_PRODUCT]}")
        return 1
    
    if product_default[INFO_PRODUCT] != product_latest[INFO_PRODUCT]:
        print(f"ERROR: Product MLB mismatch: {product_default[INFO_PRODUCT]} vs {product_latest[INFO_PRODUCT]}")
        return 1
    
    if generic_default[INFO_PRODUCT] != generic_latest[INFO_PRODUCT]:
        print(f"ERROR: Generic MLB mismatch: {generic_default[INFO_PRODUCT]} vs {generic_latest[INFO_PRODUCT]}")
        return 1
    
    if valid_latest[INFO_PRODUCT] != generic_latest[INFO_PRODUCT]:
        print(f"ERROR: Latest product mismatch: {valid_latest[INFO_PRODUCT]} vs {generic_latest[INFO_PRODUCT]}")
        return 1
    
    if product_default[INFO_PRODUCT] != valid_default[INFO_PRODUCT]:
        print(f"ERROR: Valid vs product mismatch: {product_default[INFO_PRODUCT]} vs {valid_default[INFO_PRODUCT]}")
        return 1
    
    print("SUCCESS: MLB validation algorithm working correctly!")
    return 0

def action_verify(args):
    session = get_session(args.verbose)
    
    generic_latest = get_image_info(session, RECENT_MAC, MLB_ZERO, False, 'latest')
    uvalid_default = get_image_info(session, args.board_id, args.mlb, False, 'default')
    uvalid_latest = get_image_info(session, args.board_id, args.mlb, False, 'latest')
    uproduct_default = get_image_info(session, args.board_id, product_mlb(args.mlb), False, 'default')
    
    if args.verbose:
        print("Generic latest:", json.dumps(generic_latest, indent=2))
        print("User valid default:", json.dumps(uvalid_default, indent=2))
        print("User valid latest:", json.dumps(uvalid_latest, indent=2))
        print("User product default:", json.dumps(uproduct_default, indent=2))
    
    if uvalid_default[INFO_PRODUCT] != uvalid_latest[INFO_PRODUCT]:
        status = "supported" if uvalid_latest[INFO_PRODUCT] == generic_latest[INFO_PRODUCT] else "unsupported"
        print(f"SUCCESS: MLB {args.mlb} looks valid ({status})!")
        return 0
    
    print("UNKNOWN: MLB may be invalid or very new model")
    return 0

def action_guess(args):
    mlb = args.mlb
    anon = mlb.startswith('000')
    
    try:
        with open(args.board_db, encoding='utf-8') as f:
            db = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"ERROR: Cannot load board database {args.board_db}: {e}")
        return 1
    
    session = get_session(args.verbose)
    generic_latest = get_image_info(session, RECENT_MAC, MLB_ZERO, False, 'latest')
    
    supported = {}
    
    for model, max_version in db.items():
        try:
            if anon:
                model_latest = get_image_info(session, model, MLB_ZERO, False, 'latest')
                if model_latest[INFO_PRODUCT] != generic_latest[INFO_PRODUCT]:
                    continue
                user_default = get_image_info(session, model, mlb, False, 'default')
                if user_default[INFO_PRODUCT] != generic_latest[INFO_PRODUCT]:
                    supported[model] = [max_version, user_default[INFO_PRODUCT], generic_latest[INFO_PRODUCT]]
            else:
                user_latest = get_image_info(session, model, mlb, False, 'latest')
                user_default = get_image_info(session, model, mlb, False, 'default')
                if user_latest[INFO_PRODUCT] != user_default[INFO_PRODUCT]:
                    supported[model] = [max_version, user_default[INFO_PRODUCT], user_latest[INFO_PRODUCT]]
        except Exception:
            continue
    
    if supported:
        print(f"SUCCESS: MLB {mlb} supported on:")
        for model, data in supported.items():
            print(f"- {model} (up to {data[0]}, default: {data[1]}, latest: {data[2]})")
        return 0
    
    print(f"UNKNOWN: No supported models found for MLB {mlb}")
    return 1

PRODUCTS = [
    {"name": "High Sierra (10.13)", "b": "Mac-7BA5B2D9E42DDD94", "m": "00000000000J80300", "short": "high-sierra"},
    {"name": "Mojave (10.14)", "b": "Mac-7BA5B2DFE22DDD8C", "m": "00000000000KXPG00", "short": "mojave"},
    {"name": "Catalina (10.15)", "b": "Mac-00BE6ED71E35EB86", "m": "00000000000000000", "short": "catalina"},
    {"name": "Big Sur (11.7)", "b": "Mac-2BD1B31983FE1663", "m": "00000000000000000", "short": "big-sur"},
    {"name": "Monterey (12.6)", "b": "Mac-B809C3757DA9BB8D", "m": "00000000000000000", "os_type": "latest", "short": "monterey"},
    {"name": "Ventura (13)", "b": "Mac-4B682C642B45593E", "m": "00000000000000000", "os_type": "latest", "short": "ventura"},
    {"name": "Sonoma (14) - RECOMMENDED", "b": "Mac-827FAC58A8FDFA22", "m": "00000000000000000", "short": "sonoma"},
    {"name": "Sequoia (15)", "b": "Mac-7BA5B2D9E42DDD94", "m": "00000000000000000", "short": "sequoia"},
    {"name": "Tahoe (26)", "b": "Mac-CFF7D910A743CAAF", "m": "00000000000000000", "os_type": "latest", "short": "tahoe"},
]

def select_product(args) -> argparse.Namespace:
    for i, product in enumerate(PRODUCTS):
        print(f"{i+1}. {product['name']}")
    
    if args.shortname:
        for i, product in enumerate(PRODUCTS):
            if product.get('short') == args.shortname:
                return argparse.Namespace(
                    mlb=product["m"], 
                    board_id=product["b"], 
                    diagnostics=False, 
                    os_type=product.get("os_type", "default"),
                    verbose=False, 
                    basename="", 
                    outdir="."
                )
    
    try:
        index = int(input(f"\nChoose product (1-{len(PRODUCTS)}): ")) - 1
        product = PRODUCTS[index]
        return argparse.Namespace(
            mlb=product["m"], 
            board_id=product["b"], 
            diagnostics=False, 
            os_type=product.get("os_type", "default"),
            verbose=False, 
            basename="", 
            outdir="."
        )
    except (ValueError, IndexError):
        print("Invalid selection")
        sys.exit(1)

def main():
    parser = argparse.ArgumentParser(description="Download macOS recovery images")
    parser.add_argument('--action', choices=['download', 'selfcheck', 'verify', 'guess'], 
                       default='', help="Action to perform")
    parser.add_argument('-o', '--outdir', type=str, default='com.apple.recovery.boot')
    parser.add_argument('-n', '--basename', type=str, default='')
    parser.add_argument('-b', '--board-id', type=str, default=RECENT_MAC)
    parser.add_argument('-m', '--mlb', type=str, default=MLB_ZERO)
    parser.add_argument('-e', '--code', type=str, default='')
    parser.add_argument('--os-type', type=str, default='default', choices=['default', 'latest'])
    parser.add_argument('--diagnostics', action='store_true')
    parser.add_argument('-s', '--shortname', type=str, default='')
    parser.add_argument('-v', '--verbose', action='store_true')
    parser.add_argument('-db', '--board-db', type=str, 
                       default=str(SELF_DIR / 'boards.json'))

    args = parser.parse_args()

    if args.code:
        args.mlb = mlb_from_eeee(args.code)

    if len(args.mlb) != 17:
        print("ERROR: MLB must be 17 characters")
        return 1

    try:
        if args.action == 'download':
            return action_download(args)
        elif args.action == 'selfcheck':
            return action_selfcheck(args)
        elif args.action == 'verify':
            return action_verify(args)
        elif args.action == 'guess':
            return action_guess(args)
        else:
            download_args = select_product(args)
            return action_download(download_args)
    except MacRecoveryError as e:
        print(f"ERROR: {e}")
        return 1
    except KeyboardInterrupt:
        print("\nAborted")
        return 1

if __name__ == '__main__':
    sys.exit(main())
