#!/usr/bin/env bash
cd "$(dirname "$0")"

PIDFILE="qemu-vm.pid"

if [ -f "$PIDFILE" ] && kill -0 "$(cat "$PIDFILE")" 2>/dev/null; then
  echo "Running (PID $(cat "$PIDFILE"))."
  ps -o pid,etime,pcpu,pmem,cmd -p "$(cat "$PIDFILE")" | tail -1
else
  echo "Stopped."
fi
