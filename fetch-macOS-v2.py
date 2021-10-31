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

import os
import sys
import json
import random
import argparse

try:
    from urllib.request import Request, urlopen
    from urllib.parse import urlparse
except ImportError:
    from urllib2 import Request, urlopen
    from urlparse import urlparse

SELF_DIR = os.path.dirname(os.path.realpath(__file__))

RECENT_MAC = 'Mac-7BA5B2D9E42DDD94'
MLB_ZERO = '00000000000000000'
MLB_VALID = 'C02749200YGJ803AX'
MLB_PRODUCT = '00000000000J80300'

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
INFO_REQURED = [INFO_PRODUCT, INFO_IMAGE_LINK, INFO_IMAGE_HASH, INFO_IMAGE_SESS,
                INFO_SIGN_LINK, INFO_SIGN_HASH, INFO_SIGN_SESS]


def run_query(url, headers, post=None, raw=False):
    if post is not None:
        data = '\n'.join([entry + '=' + post[entry] for entry in post])
        if sys.version_info[0] >= 3:
            data = data.encode('utf-8')
    else:
        data = None

    req = Request(url=url, headers=headers, data=data)
    response = urlopen(req)
    if raw:
        return response
    return dict(response.info()), response.read()


def generate_id(itype, nid=None):
    valid_chars = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9', 'A', 'B', 'C', 'D', 'E', 'F']
    if nid is None:
        return ''.join(random.choice(valid_chars) for i in range(itype))
    return nid


def product_mlb(mlb):
    return '00000000000' + mlb[11] + mlb[12] + mlb[13] + mlb[14] + '00'


def mlb_from_eeee(eeee):
    if len(eeee) != 4:
        print('ERROR: Invalid EEEE code length!')
        sys.exit(1)

    return '00000000000' + eeee + '00'

def get_session(args):
    headers = {
        'Host': 'osrecovery.apple.com',
        'Connection': 'close',
        'User-Agent': 'InternetRecovery/1.0',
    }

    headers, output = run_query('http://osrecovery.apple.com/', headers)

    if args.verbose:
        print('Session headers:')
        for header in headers:
            print('{}: {}'.format(header, headers[header]))

    for header in headers:
        if header.lower() == 'set-cookie':
            cookies = headers[header].split('; ')
            for cookie in cookies:
                if cookie.startswith('session='):
                    return cookie

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

    if sys.version_info[0] >= 3:
        output = output.decode('utf-8')

    info = {}
    for line in output.split('\n'):
        try:
            key, value = line.split(': ')
            info[key] = value
        except:
            continue

    for k in INFO_REQURED:
        if k not in info:
            raise RuntimeError('Missing key ' + k)

    return info


def save_image(url, sess, filename='', directory=''):
    purl = urlparse(url)
    headers = {
        'Host': purl.hostname,
        'Connection': 'close',
        'User-Agent': 'InternetRecovery/1.0',
        'Cookie': '='.join(['AssetToken', sess])
    }

    if filename == '':
        filename = os.path.basename(purl.path)
    if filename.find('/') >= 0 or filename == '':
        raise RuntimeError('Invalid save path ' + filename)

    print('Saving ' + url + ' to ' + filename + '...')

    with open(os.path.join(directory, filename), 'wb') as fhandle:
        response = run_query(url, headers, raw=True)

        total_size = int(response.headers['content-length']) / float(2 ** 20)
        # print(total_size)
        if total_size < 1:
            total_size = response.headers['content-length']
            print("Note: The total download size is %s bytes" % total_size)
        else:
            print("Note: The total download size is %0.2f MB" % total_size)
        size = 0
        while True:
            chunk = response.read(2 ** 20)
            if not chunk:
                break
            fhandle.write(chunk)
            size += len(chunk)
            print('\r{} MBs downloaded...'.format(size / (2 ** 20)), end='')
            sys.stdout.flush()
        print('\rDownload complete!' + ' ' * 32)


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
    info = get_image_info(session, bid=args.board_id, mlb=args.mlb,
                          diag=args.diagnostics, os_type=args.os_type)
    if args.verbose:
        print(info)
    print('Downloading ' + info[INFO_PRODUCT] + '...')
    dmgname = '' if args.basename == '' else args.basename + '.dmg'
    save_image(info[INFO_IMAGE_LINK], info[INFO_IMAGE_SESS], dmgname, args.outdir)
    cnkname = '' if args.basename == '' else args.basename + '.chunklist'
    save_image(info[INFO_SIGN_LINK], info[INFO_SIGN_SESS], cnkname, args.outdir)
    return 0


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
    valid_default = get_image_info(session, bid=RECENT_MAC, mlb=MLB_VALID,
                                   diag=False, os_type='default')
    valid_latest = get_image_info(session, bid=RECENT_MAC, mlb=MLB_VALID,
                                  diag=False, os_type='latest')
    product_default = get_image_info(session, bid=RECENT_MAC, mlb=MLB_PRODUCT,
                                     diag=False, os_type='default')
    product_latest = get_image_info(session, bid=RECENT_MAC, mlb=MLB_PRODUCT,
                                    diag=False, os_type='latest')
    generic_default = get_image_info(session, bid=RECENT_MAC, mlb=MLB_ZERO,
                                     diag=False, os_type='default')
    generic_latest = get_image_info(session, bid=RECENT_MAC, mlb=MLB_ZERO,
                                    diag=False, os_type='latest')

    if args.verbose:
        print(valid_default)
        print(valid_latest)
        print(product_default)
        print(product_latest)
        print(generic_default)
        print(generic_latest)

    if valid_default[INFO_PRODUCT] == valid_latest[INFO_PRODUCT]:
        # Valid MLB must give different default and latest if this is not a too new product.
        print('ERROR: Cannot determine any previous product, got {}'.format(valid_default[INFO_PRODUCT]))
        return 1

    if product_default[INFO_PRODUCT] != product_latest[INFO_PRODUCT]:
        # Product-only MLB must give the same value for default and latest.
        print('ERROR: Latest and default do not match for product MLB, got {} and {}'.format(
            product_default[INFO_PRODUCT], product_latest[INFO_PRODUCT]))
        return 1

    if generic_default[INFO_PRODUCT] != generic_latest[INFO_PRODUCT]:
        # Zero MLB always give the same value for default and latest.
        print('ERROR: Generic MLB gives different product, got {} and {}'.format(
            generic_default[INFO_PRODUCT], generic_latest[INFO_PRODUCT]))
        return 1

    if valid_latest[INFO_PRODUCT] != generic_latest[INFO_PRODUCT]:
        # Valid MLB must always equal generic MLB.
        print('ERROR: Cannot determine unified latest product, got {} and {}'.format(
            valid_latest[INFO_PRODUCT], generic_latest[INFO_PRODUCT]))
        return 1

    if product_default[INFO_PRODUCT] != valid_default[INFO_PRODUCT]:
        # Product-only MLB can give the same value with valid default MLB.
        # This is not an error for all models, but for our chosen code it is.
        print('ERROR: Valid and product MLB give mismatch, got {} and {}'.format(
            product_default[INFO_PRODUCT], valid_default[INFO_PRODUCT]))
        return 1

    print('SUCCESS: Found no discrepancies with MLB validation algorithm!')
    return 0


def action_verify(args):
    """
    Try to verify MLB serial number.
    """
    session = get_session()
    generic_latest = get_image_info(session, bid=RECENT_MAC, mlb=MLB_ZERO,
                                    diag=False, os_type='latest')
    uvalid_default = get_image_info(session, bid=args.board_id, mlb=args.mlb,
                                    diag=False, os_type='default')
    uvalid_latest = get_image_info(session, bid=args.board_id, mlb=args.mlb,
                                   diag=False, os_type='latest')
    uproduct_default = get_image_info(session, bid=args.board_id, mlb=product_mlb(args.mlb),
                                      diag=False, os_type='default')

    if args.verbose:
        print(generic_latest)
        print(uvalid_default)
        print(uvalid_latest)
        print(uproduct_default)

    # Verify our MLB number.
    if uvalid_default[INFO_PRODUCT] != uvalid_latest[INFO_PRODUCT]:
        if uvalid_latest[INFO_PRODUCT] == generic_latest[INFO_PRODUCT]:
            print('SUCCESS: {} MLB looks valid and supported!'.format(args.mlb))
        else:
            print('SUCCESS: {} MLB looks valid, but probably unsupported!'.format(args.mlb))
        return 0

    print('UNKNOWN: Run selfcheck, check your board-id, or try again later!')

    # Here we have matching default and latest products. This can only be true for very
    # new models. These models get either latest or special builds.
    if uvalid_default[INFO_PRODUCT] == generic_latest[INFO_PRODUCT]:
        print('UNKNOWN: {} MLB can be valid if very new!'.format(args.mlb))
        return 0
    if uproduct_default[INFO_PRODUCT] != uvalid_default[INFO_PRODUCT]:
        print('UNKNOWN: {} MLB looks invalid, other models use product {} instead of {}!'.format(
            args.mlb, uproduct_default[INFO_PRODUCT], uvalid_default[INFO_PRODUCT]))
        return 0
    print('UNKNOWN: {} MLB can be valid if very new and using special builds!'.format(args.mlb))
    return 0


def action_guess(args):
    """
    Attempt to guess which model does this MLB belong.
    """

    mlb = args.mlb
    anon = mlb.startswith('000')

    with open(args.board_db, 'r') as fhandle:
        db = json.load(fhandle)

    supported = {}

    session = get_session(args)

    generic_latest = get_image_info(session, bid=RECENT_MAC, mlb=MLB_ZERO,
                                    diag=False, os_type='latest')

    for model in db:
        try:
            if anon:
                # For anonymous lookup check when given model does not match latest.
                model_latest = get_image_info(session, bid=model, mlb=MLB_ZERO,
                                              diag=False, os_type='latest')

                if model_latest[INFO_PRODUCT] != generic_latest[INFO_PRODUCT]:
                    if db[model] == 'current':
                        print('WARN: Skipped {} due to using latest product {} instead of {}'.format(
                            model, model_latest[INFO_PRODUCT], generic_latest[INFO_PRODUCT]))
                    continue

                user_default = get_image_info(session, bid=model, mlb=mlb,
                                              diag=False, os_type='default')

                if user_default[INFO_PRODUCT] != generic_latest[INFO_PRODUCT]:
                    supported[model] = [db[model], user_default[INFO_PRODUCT], generic_latest[INFO_PRODUCT]]
            else:
                # For normal lookup check when given model has mismatching normal and latest.
                user_latest = get_image_info(session, bid=model, mlb=mlb,
                                             diag=False, os_type='latest')

                user_default = get_image_info(session, bid=model, mlb=mlb,
                                              diag=False, os_type='default')

                if user_latest[INFO_PRODUCT] != user_default[INFO_PRODUCT]:
                    supported[model] = [db[model], user_default[INFO_PRODUCT], user_latest[INFO_PRODUCT]]

        except Exception as e:
            print('WARN: Failed to check {}, exception: {}'.format(model, str(e)))

    if len(supported) > 0:
        print('SUCCESS: MLB {} looks supported for:'.format(mlb))
        for model in supported:
            print('- {}, up to {}, default: {}, latest: {}'.format(model, supported[model][0],
                                                                   supported[model][1], supported[model][2]))
        return 0

    print('UNKNOWN: Failed to determine supported models for MLB {}!'.format(mlb))


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
    parser.add_argument('-o', '--outdir', type=str, default=os.getcwd(),
                        help='customise output directory for downloading, defaults to current directory')
    parser.add_argument('-n', '--basename', type=str, default='',
                        help='customise base name for downloading, defaults to remote name')
    parser.add_argument('-b', '--board-id', type=str, default=RECENT_MAC,
                        help='use specified board identifier for downloading, defaults to ' + RECENT_MAC)
    parser.add_argument('-m', '--mlb', type=str, default=MLB_ZERO,
                        help='use specified logic board serial for downloading, defaults to ' + MLB_ZERO)
    parser.add_argument('-e', '--code', type=str, default='',
                        help='generate product logic board serial with specified product EEEE code')
    parser.add_argument('-os', '--os-type', type=str, default='default', choices=['default', 'latest'],
                        help='use specified os type, defaults to default ' + MLB_ZERO)
    parser.add_argument('-diag', '--diagnostics', action='store_true', help='download diagnostics image')
    parser.add_argument('-s', '--shortname', type=str, default='',
                        help='available options: high-sierra, mojave, catalina, big-sur, monterey')
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
    products = [
            {"name": "High Sierra (10.13)", "b": "Mac-7BA5B2D9E42DDD94", "m": "00000000000J80300", "short": "high-sierra"},
            {"name": "Mojave (10.14)", "b": "Mac-7BA5B2DFE22DDD8C", "m": "00000000000KXPG00", "short": "mojave"},
            {"name": "Catalina (10.15)", "b": "Mac-00BE6ED71E35EB86", "m": "00000000000000000", "short": "catalina"},
            {"name": "Big Sur (11.6) - RECOMMENDED", "b": "Mac-2BD1B31983FE1663", "m": "00000000000000000", "short": "big-sur"},
            {"name": "Monterey (latest)", "b": "Mac-7BA5B2D9E42DDD94", "m": "00000000000000000", "os_type": "latest", "short": "monterey"}
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



    # action
    product = products[index]
    print(product['name'])
    try:
        os_type = product["os_type"]
    except:
        os_type = "default"
    args = gdata(mlb = product["m"], board_id = product["b"], diagnostics =
            False, os_type = os_type, verbose=False, basename="", outdir=".")
    action_download(args)


if __name__ == '__main__':
    sys.exit(main())
