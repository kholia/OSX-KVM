#!/usr/bin/env bash
cd "$(dirname "$0")"

PIDFILE="qemu-vm.pid"
SOCK="qemu-monitor.sock"

if [ ! -f "$PIDFILE" ] || ! kill -0 "$(cat "$PIDFILE")" 2>/dev/null; then
  echo "VM not running."
  rm -f "$PIDFILE"
  exit 0
fi

PID="$(cat "$PIDFILE")"

if [ -S "$SOCK" ] && [ "$1" != "--force" ]; then
  echo "Sending graceful shutdown (system_powerdown) via QEMU monitor..."
  echo "system_powerdown" | socat - "UNIX-CONNECT:$SOCK" >/dev/null 2>&1 || true

  for i in $(seq 1 60); do
    if ! kill -0 "$PID" 2>/dev/null; then
      echo "VM shut down cleanly."
      rm -f "$PIDFILE" "$SOCK"
      exit 0
    fi
    sleep 2
  done
  echo "VM did not shut down within 120s."
fi

if [ "$1" == "--force" ]; then
  echo "Force killing PID $PID."
  kill -9 "$PID" 2>/dev/null || true
  rm -f "$PIDFILE" "$SOCK"
else
  echo "Guest didn't power off in time. Re-run with --force to hard-kill it (may corrupt disk state)."
  exit 1
fi
