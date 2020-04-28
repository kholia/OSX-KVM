#!/usr/bin/env python

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
