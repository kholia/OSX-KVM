#!/usr/bin/env python
#
# NOTE -> https://github.com/kholia/OSX-KVM/blob/master/reversing-notes.md
#
# https://github.com/radareorg/radare2-r2pipe/blob/master/python/examples/libgraph.py
# https://github.com/radareorg/radare2-r2pipe/tree/master/python
#
# https://www.hex-rays.com/wp-content/uploads/2019/12/xnu_debugger_primer.pdf
# https://geosn0w.github.io/Debugging-macOS-Kernel-For-Fun/
#
# sudo apt-get install radare2  # Ubuntu 20.04 LTS
# pip install r2pipe
#
# This software is Copyright (c) 2020, Dhiru Kholia. This program is provided
# for educational, research, and non-commercial personal use only.
# !!! ATTENTION !!! Any commercial usage against the Apple EULA is at your own
# risk!
#
# Note: Commercial usage and redistribution is forbidden (not allowed).
#
# THIS SOFTWARE IS PROVIDED BY <COPYRIGHT HOLDER> 'AS IS' AND ANY EXPRESS OR
# IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF
# MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO
# EVENT SHALL <COPYRIGHT HOLDER> BE LIABLE FOR ANY DIRECT, INDIRECT,
# INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
# LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA,
# OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF
# LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING
# NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE,
# EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
#
# $ ./kernel_autopatcher.py kernel
# [+] Processing <kernel> file...
# [+] Patching done!
#
# (Re)Tested against the default "kernel" from macOS Catalina 10.15.7 in
# October, 2020.
#
# Note: Disable SIP on the macOS VM (We do it via OpenCore's config.plist)
# `00000000` - SIP completely enabled
# `30000000` - Allow unsigned kexts and writing to protected fs locations
# `67000000` - SIP completely disabled
#
# Note: sudo mount -uw /
#
# Kernel location (Catalina): /System/Library/Kernels/kernel
#
# $ md5sum kernel*
# 3966d407c344708d599500c60c1194c0  kernel
# 8530d3422795652ed320293ecc127770  kernel.patched
#
# Test command -> sudo /usr/bin/AssetCacheManagerUtil activate

import r2pipe

import sys
import os


def patcher(fname):
    target_symbol = "sym._cpuid_get_feature_names"

    # analysis code
    # r2 = r2pipe.open(fname, ["-2"])  # -2 -> disable stderr messages
    r2 = r2pipe.open(fname, ["-2", "-w"])  # -2 -> disable stderr messages
    print("[+] Processing <%s> file..." % fname)
    r2.cmd('aa')
    # print(r2.cmd("pdf @ sym._cpuid_get_feature_names"))
    result = r2.cmdj("axtj %s" % target_symbol)
    if not result:
        print("[!] Can't find xrefs to <%s>. Aborting!" % target_symbol)
        sys.exit(2)
    # print(result)
    r2.cmd("s `axt sym._cpuid_get_feature_names~[1]`")  # jump to the function call site
    result = r2.cmdj("pdj 1")
    if not result:
        print("[!] Can't disassemble instruction at function call site. Aborting!")
        sys.exit(3)
    opcode_size = result[0]["size"]
    assert (opcode_size == 5)  # sanity check, call sym._cpuid_get_feature_name -> 5 bytes

    # patching code
    # > pa nop
    r2.cmd("\"wa nop;nop;nop;nop;nop\"")
    r2.quit()
    print("[+] Patching done!")


if __name__ == "__main__":
    if len(sys.argv) > 1:
        path = sys.argv[1]
        patcher(path)
    else:
        print("Usage: %s [path-to-kernel-file]" % (sys.argv[0]))
        sys.exit(1)
