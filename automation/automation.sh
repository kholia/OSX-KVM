#!/usr/bin/env bash
if [[ $0 = "${BASH_SOURCE[0]}" ]]; then
set -euo pipefail
fi

function === { echo "=== $*" >&2; }

vncsend() { vncdo -s localhost:1 "$@"; }

# proxy all those commands
commands=(
  capture
  click
  expect
  key
  move
)
for cmd in "${commands[@]}"; do
  eval "$cmd() { vncsend $cmd \"\$@\"; }"
done

# rename type to text to avoid overriding the `type` builtin
text() {
  vncsend type "$@"
}

expect() {
  local img=$1 imgtmp imgdiff
  imgtmp=$(mktemp XXXXXXXX.png)
  imgdiff=$(mktemp XXXXXXXXX-diff.png)
  capture "$imgtmp"
  compare \
    -metric AE -fuzz 5% \
    "$img" "$imgtmp" \
    -compose Src \
    "$imgdiff"

  # TODO: calculate the number of red pixels
}

expect() {
  echo "wait for the screen to look like $1"
  img2txt -W 79 "$1"
  read -r
}

if [[ $0 != "${BASH_SOURCE[0]}" ]]; then
  return
fi

### Main ###
# TODO: start qemu as well

# TODO: allow to jump forward to resume the installation from a certain point

=== Starting VNC viewer for debugging

vncviewer -noraiseonbeep localhost:1 &
pid=$!
trap 'kill $pid' EXIT
# rm mac_hdd_ng.img
# qemu-img create -f qcow2 mac_hdd_ng.img 32G

# TODO: also start qemu
#exec {myfd}< <(./boot-macOS-NG.sh)

=== Boot installer
expect cap1.png 0
key enter

=== Language selection
# NOTE: this is remembered
expect cap1.1.png 0

# spam enter, doesn't seem reliable
key enter
key enter
key enter

=== Select the disk utility
expect cap2.png 0
# selected safari instead one time
key down
key down
key down
key down
key tab
key space

=== Select qemu HDD
expect cap3.png 0
key up

=== Select erase button
# FIXME: partition buttons got selected instead
key tab
key tab
key tab
key space

=== Enter disk info
# FIXME: for some reason it typed "mACINTOSH hd"
# text "Macintosh HD"
# Theory: only use lower cases to avoid that issue
text "macos"
key tab
key tab
key tab
key tab
key tab
key space

=== Back to menu
expect cap4.png 0
move 80 10 click 1
key q
# FIXME: this is not reliable. spam
key space
key space
key space

=== Start the installer
expect cap2.png 10
key up
key up
key tab
key space

=== macOS Mojave
# FIXME: It can output the following error:
#        "The request to the recovery server timed out."
#        => cap5-error.png
expect cap5.png 10
key tab
key space

=== macOS license
expect cap6.png 10
key tab
key tab
key space

=== macOS license popup
expect cap6.1.png 10
key tab
key space

=== disk selector
expect cap7.png 10
# disk not selectable through keyboard presses
move 450 500 click 1
# aand now the button is not navigable either
move 560 620 click 1

# wait 17 minutes
=== select country
# FIXME: sometimes the installed fails
# cap8-error.png
expect cap8.png 10
move 500 500 click 1
key v
key up
key up
key up
key tab
key space

=== select keyboard
expect cap9.png 10
key tab
key tab
key tab
key space

=== data and privacy
expect cap10.png 10
key tab
key tab
key tab
key space

=== transfer information to this mac
expect cap11.png 10
key tab
key tab
key tab
key space

=== sign in with your Apple ID
expect cap12.png 10
key tab
key tab
key tab
key tab
key tab
key tab
key space
key tab
key space

=== terms and conditions
expect cap13.png 10
key tab
key tab
key space
# popup
key tab
key space

=== create a computer account
expect cap14.png 10
text user
key tab
key tab
text password
key tab
text password
key tab
key tab
key tab
key space

=== express setup
expect cap15.png 10
key tab
key tab
key space

=== enable location services
expect cap16.png 10
key tab
key tab
key tab
key tab
key space
# popup
key tab
key space

=== select your timezone
expect cap17.png 10
key tab
key tab
key tab
key tab
key space

=== analytics
expect cap18.png 10
key tab
key space
key tab
key tab
key tab
key space

=== choose your look
expect cap19.png 10
key tab
key tab
key tab
key space

=== started!
expect cap20.png 10

# TODO: make meta-space work
key meta-space
text "terminal"
key enter

text "sudo systemsetup -setremotelogin on"
key enter
text "password"
key enter

# (qemu) savevm prepare
# Error: State blocked by non-migratable CPU device (invtsc flag)

# Error: Device 'pflash1' is writable but does not support snapshots
