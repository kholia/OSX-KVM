#!/usr/bin/env bash
set -e
cd "$(dirname "$0")"

PIDFILE="qemu-vm.pid"

if [ -f "$PIDFILE" ] && kill -0 "$(cat "$PIDFILE")" 2>/dev/null; then
  echo "VM already running (PID $(cat "$PIDFILE"))."
  exit 0
fi

rm -f qemu-monitor.sock

nohup ./OpenCore-Boot.sh > boot.log 2>&1 < /dev/null &
echo $! > "$PIDFILE"
disown

echo "VM starting (PID $(cat "$PIDFILE"))."
echo "VNC: this-host:5901  |  SSH: this-host:2222  |  Screen Sharing: this-host:5900"
