#!/bin/bash

# Script for building bootable .iso images from downloaded macOS upgrade
# Copyright (C) 2015-2017 Karlson2k (Evgeny Grin)
#
# You can run, copy, modify, publish and do whatever you want with this
# script as long as this message and copyright string above are preserved.
# You are also explicitly allowed to reuse this script under any LGPL or
# GPL license or under any BSD-style license.
#
#
# Latest version:
# https://raw.githubusercontent.com/Karlson2k/k2k-OSX-Tools/master/Create_osx_install_iso/create_osx_install_iso.sh
#
# Version 1.0.6 + local changes

function myreadlink() {
  (
    cd $(dirname $1)
    if [[ -L $1 ]] ; then
        cd $(dirname $(readlink $1))
    else
        cd $(dirname $1)
    fi
    echo $PWD/$(basename $1)
  )
}

readonly script_org_name='create_install_iso.sh' || exit 127
unset work_dir script_name tmp_dir OSX_inst_name OSX_inst_inst_dmg_mnt \
	OSX_inst_img_rw_mnt OSX_inst_img_rw_dev || exit 127
work_dir="$PWD"
script_dir="$(dirname $(myreadlink "$0"))"
cd "$work_dir"
save_IFS="$IFS" || exit 127
export LANG='en_US.UTF-8' || exit 127 # prevent localization of output, not really required

[[ `ps -o comm -p $$ | tail -n1 2>/dev/null` =~ bash$ ]] || {
	echo "Script is designed to be run only with bash"
	exit 127
}
[[ "$(uname -s)" == Darwin ]] || {
	echo "Script can be run only on Mac OS X"
	exit 127
}

cleanup() {
	trap - SIGHUP SIGTERM SIGQUIT SIGINT SIGSTOP SIGTSTP EXIT
	if [[ -n $tmp_dir ]] && [[ -e "$tmp_dir" ]]; then
		if [[ -e "$OSX_inst_img_rw_dev" ]]; then
			echo "Unmounting writable image..."
			hdiutil detach "$OSX_inst_img_rw_dev" -force
		fi
		if [[ -e "$OSX_inst_img_rw_mnt" ]]; then
			echo "Unmounting writable image..."
			hdiutil detach "$OSX_inst_img_rw_mnt" -force
		fi
		if [[ -e "$OSX_inst_inst_dmg_mnt" ]]; then
			echo "Unmounting temporary mounted source image..."
			hdiutil detach "$OSX_inst_inst_dmg_mnt" -force
		fi
		echo "Removing temporary files..."
		rm -fdR "$tmp_dir"
	fi
}

trap '{ exit_code="$?"; cleanup; exit $exit_code; }' EXIT

echo_term_ansi_m() {
	local n_param=''
	if [[ "$1" == "-n" ]]; then
		n_param="$1"
		shift
	elif [[ -z "$1" ]]; then shift
	fi
	local m_code="$1"
	shift
	if [[ -t 1 ]]; then
		echo $n_param $'\e['"${m_code}m$@"$'\e[0m'
	else
		echo $n_param "$@"
	fi
}

echo_neutral() {
	echo "$@"
}

echo_enh() {
	echo_term_ansi_m '1;97' "$@"
}

echo_enh_n() {
	echo_term_ansi_m -n '1;97' "$@"
}

echo_positive() {
	echo_term_ansi_m '1;92' "$@"
}

echo_positive_n() {
	echo_term_ansi_m -n '1;92' "$@"
}

echo_warning() {
	echo_term_ansi_m '1;93' "$@"
}

echo_warning_n() {
	echo_term_ansi_m -n '1;93' "$@"
}

echo_error() {
	echo_term_ansi_m '1;91' "$@" 1>&2
}
echo_error_n() {
	echo_term_ansi_m -n '1;91' "$@" 1>&2
}

exit_with_error() {
	trap - SIGHUP SIGTERM SIGQUIT SIGINT SIGSTOP SIGTSTP EXIT
	if [[ -n $1 ]]; then
		echo_error "Error: $1"
	else
		echo_error "Error."
	fi
	cleanup
    [[ $2 > 0 ]] && exit $2
    exit 1
}

trap '{ exit_with_error "unexpected interrupt at line $LINENO"; exit 255; }' SIGHUP SIGTERM SIGQUIT SIGINT SIGSTOP SIGTSTP

# trap 'echo "Line number: $LINENO"; read -p "\"Enter\" to continue" ' DEBUG

stage_start() {
	echo_enh_n "$@... "
}

stage_start_nl() {
	stage_start "$@"
	echo ''
}

stage_end_ok() {
	if [[ -z "$@" ]]; then
		echo_positive "OK"
	else
	    echo_positive "$@"
	fi
}

stage_end_warn() {
	if [[ -z "$@" ]]; then
		echo_warning "OK, but with warnings"
	else
	    echo_warning "$@"
	fi
}

is_answer_valid() {
	local answ="$1"
	shift
	while [[ -n $1 ]]; do
		[[ "$answ" == "$1" ]] && return 0
		shift
	done
	return 1
}

script_name="$(basename "${BASH_SOURCE[0]}" 2>/dev/null)"
[[ -n "$script_name" ]] || script_name="${0##*/}" # fallback
[[ -n "$script_name" ]] || script_name="${script_org_name}" # second fallback

script_version="$(sed -n -e '\|^# Version| {s|^# Version \(.*$\)|\1|p; q;}' "${BASH_SOURCE[0]}" 2>/dev/null)" || unset script_version
[[ -n "$script_version" ]] || script_version="Unknown"

print_help() {
	echo "\
Script for creating .iso images from downloaded macOS upgrade application.
Usage:"
	echo_enh_n "      $script_name"; echo " [options]

Valid options are:
      -a, --app[lication] <macOS Install app>
                   Path and name of macOS upgrade application.
                   Path can be omitted if application is located at
                   default path.
      -i, --iso <path with name for .iso>
                   Path with optional name for output .iso
      -m, --method <D>
                   Use method number D to create installation image:
                   Method 1 create image that most close to Apple's image,
                   but potentially less compatible with some BIOSes/EFI.
                   Method 2 create more BIOS/EFI-friendly images, but
                   require more disk space for conversion.
                   Method 3 can produce bootable images without super
                   user rights.
      -n, --nosudo
                   Do not use sudo command (untested, unsupported)
      -v, --verify
                   Do not skip verifications (slow down image creation)
      -h, --help   Print this message and exit
      -V, --version
                   Print version information and exit"

}

print_version() {
	echo "${script_org_name} version $script_version"
}

exit_with_cmd_err() {
	echo_error "$@"
	print_help 1>&2
	exit 32
}

unset cmd_par_app cmd_par_iso test_name ver_opt cr_method || exit_with_error "Can't unset variable"
# allow_sudo='yes' && ver_opt='--noverify' || exit_with_error "Can't set variable"
ver_opt='--noverify'
inject_kexts='no'
while [[ -n "$1" ]]; do
	case "$1" in
		-a | --app | --application ) cmd_par_app="$2"
			[[ -n "$cmd_par_app" ]] && [[ "$cmd_par_app" != "--iso" ]] || exit_with_cmd_err "No Application name given for $1"
			shift 2 ;;
		-i | --iso ) cmd_par_iso="$2"
			[[ -n "$cmd_par_iso" ]] && [[ "$cmd_par_iso" != "--app" ]] || exit_with_cmd_err "No .iso name given for $1"
			shift 2 ;;
		-m | --method ) [[ -z "$2" ]] && exit_with_cmd_err "Method not specified for $1"
			cr_method="method${2}"
			shift 2 ;;
		-m* ) cr_method="method${1#-m}"; shift ;;
		--method* ) cr_method="method${1#--method}"; shift ;;
		-n | --nosudo ) allow_sudo='no'; shift ;;
		-v | --verify ) unset ver_opt; shift ;;
		-k ) inject_kexts='yes'; shift ;;
		-h | --h | --help ) print_help; exit 0 ;;
		-V | --version ) print_version; exit 0 ;;
		*) exit_with_cmd_err "Unknown option \"$1\""
	esac
done

[[ "${cr_method-notset}" == "notset" ]] || [[ "$cr_method" =~ ^"method"[1-3]$ ]] || exit_with_cmd_err "Unknown creation method specified: ${cr_method#method}"

check_intall_app() {
	[[ -n "$1" ]] || return 3
	[[ -d "$1" ]] || return 2
	[[ -e "$1/Contents/SharedSupport/InstallESD.dmg" ]] || return 1
	return 0
}

if [[ -z "$cmd_par_app" ]]; then
	stage_start "Looking for downloaded OS upgrades"
	unset test_name || exit_with_error
	IFS=$'\n'
	dirlist=(`find /Applications -maxdepth 1 -mindepth 1 \( -name 'Install OS X *.app' -or -name 'Install macOS *.app' \)`) || exit_with_error "Can't find downloaded macOS upgrade"
	IFS="$save_IFS"
	[[ ${#dirlist[@]} -eq 0 ]] && exit_with_error "Can't find downloaded OS X / macOS upgrade. Use the -a option to specify the path to it manually."
	stage_end_ok "found"
	if [[ ${#dirlist[@]} -gt 1 ]]; then
		echo "Several OS upgrades were found."
		echo "Which one OS upgrade do you want to use?"
		valid_answers=()
		unset test_name || exit_with_error
		for ((i=0;i<${#dirlist[@]};i++)); do
			test_name="${dirlist[$i]#/Applications/Install }"
			echo "$((i+1))) ${test_name%.app}"
			valid_answers[$i]="$((i+1))"
		done
		read -n 1 -p "[1-$i, q for quit]: " answer
		echo ''
		until is_answer_valid $answer ${valid_answers[@]} 'q'; do
			echo "'$answer' is incorrect response"
			read -n 1 -p "Select ""$(seq -s ', ' -t '\b\b' 1 $i)"" or q for quit: " answer
			echo ''
		done
		[[ "$answer" == "q" ]] && { echo_warning "Aborted."; exit 2; }
		OSX_inst_app="${dirlist[$((answer-1))]}"
	else
		OSX_inst_app="${dirlist[0]}"
	fi
	echo_enh "Using \"$OSX_inst_app\"."
else
	stage_start "Checking for specified OS upgrade"
	unset OSX_inst_app || exit_with_error
	if check_intall_app "${cmd_par_app%/}"; then
		# direct location with path
		if [[ "${cmd_par_app:0:1}" == "/" ]]; then
			OSX_inst_app="${cmd_par_app%/}" # absolute path
		else
			OSX_inst_app="$(pwd)/${cmd_par_app%/}" # relative path
			test_name="$(cd "$OSX_inst_app/" 2>/dev/null && pwd)" || unset test_name || exit_with_error
			[[ -n "$test_name" ]] && OSX_inst_app="$test_name" # use absolute path if possible
		fi
	elif [[ "${cmd_par_app%%/*}" == "${cmd_par_app%/}" ]]; then
		# check /Applications
		test_name="${cmd_par_app%/}"
		test_name="${test_name%.app}.app"
		if check_intall_app "/Applications/${test_name}"; then
			OSX_inst_app="/Applications/${test_name}"
		elif check_intall_app "/Applications/Install ${test_name}"; then
			OSX_inst_app="/Applications/Install ${test_name}"
		elif check_intall_app "/Applications/Install OS X ${test_name}"; then
			OSX_inst_app="/Applications/Install OS X ${test_name}"
		elif check_intall_app "/Applications/Install macOS ${test_name}"; then
			OSX_inst_app="/Applications/Install macOS ${test_name}"
		fi
	fi
	[[ -n "$OSX_inst_app" ]] || exit_with_error "\"$cmd_par_app\" is not valid macOS Install application"
	stage_end_ok "found"
	echo_enh "Using \"$OSX_inst_app\"."
fi

stage_start "Detecting macOS name for installation"
unset test_name OSX_inst_prt_name || exit_with_error
test_name=$(sed -n -e '\|<key>CFBundleDisplayName</key>| { N; s|^.*<string>\(.\{1,\}\)</string>.*$|\1|p; q; }' \
	 "$OSX_inst_app/Contents/Info.plist" 2>/dev/null) || unset test_name
if [[ -n "$test_name" ]]; then
	OSX_inst_name="${test_name#Install }"
	OSX_inst_prt_name="Install $OSX_inst_name"
	stage_end_ok "$OSX_inst_name"
else
	OSX_inst_name=$(echo "$OSX_inst_app"|sed -n -e's|^.*Install \(\(macOS|OS X\) .\{1,\}\)\.app.*$|\1|p' 2>/dev/null) || unset OSX_inst_name || exit_with_error
	[[ -z "$OSX_inst_name" ]] && OSX_inst_name="macOS"
	OSX_inst_prt_name="Install $OSX_inst_name"
	stage_end_warn "guessed \"$OSX_inst_name\""
fi

stage_start "Creating temporary directory"
tmp_dir="$(mktemp -d -t osx_iso_tmpdir_XXX)" || exit_with_error "Can't create tmp directory"
# mkdir "tmp-tmp"
# tmp_dir=$(cd tmp-tmp && pwd) || exit_with_error "Can't create tmp directory"
stage_end_ok "succeed"

stage_start_nl "Mounting InstallESD.dmg"
OSX_inst_inst_dmg="$OSX_inst_app"'/Contents/SharedSupport/InstallESD.dmg'
OSX_inst_inst_dmg_mnt="$tmp_dir/InstallESD_dmg_mnt"
hdiutil attach "$OSX_inst_inst_dmg" -kernel -readonly -nobrowse ${ver_opt+-noverify} -mountpoint "$OSX_inst_inst_dmg_mnt" || exit_with_error "Can't mount installation image. Reboot recommended before retry."
OSX_inst_base_dmg="$OSX_inst_inst_dmg_mnt/BaseSystem.dmg" || exit_with_error
stage_end_ok "Mounting succeed"

stage_start "Calculating required image size"
unset OSX_inst_inst_dmg_used_size OSX_inst_base_dmg_real_size OSX_inst_base_dmg_size || exit_with_error "Can't unset variables"
OSX_inst_inst_dmg_used_size=$(hdiutil imageinfo "$OSX_inst_inst_dmg" -plist | \
	sed -En -e '\|<key>Total Non-Empty Bytes</key>| { N; s|^.*<integer>(.+)</integer>.*$|\1|p; q; }') || unset OSX_inst_inst_dmg_used_size
OSX_inst_base_dmg_real_size=$(hdiutil imageinfo "$OSX_inst_base_dmg" -plist | \
	sed -En -e '\|<key>Total Bytes</key>| { N; s|^.*<integer>(.+)</integer>.*$|\1|p; q; }') || unset OSX_inst_base_dmg_real_size
OSX_inst_base_dmg_size=$(stat -f %z "$OSX_inst_base_dmg") || unset OSX_inst_base_dmg_size
((OSX_inst_base_dmg_size=(OSX_inst_base_dmg_size/512)*512)) # round to sector bound
if !((OSX_inst_inst_dmg_used_size)) || !((OSX_inst_base_dmg_real_size)) || !((OSX_inst_base_dmg_size)); then
	((OSX_inst_img_rw_size=10*1024*1024*1024))
	stage_end_warn "Can't calculate, will use $OSX_inst_img_rw_size ($((OSX_inst_img_rw_size/(1024*1024))) MiB)"
else
	((OSX_inst_img_rw_size=OSX_inst_base_dmg_real_size+(OSX_inst_inst_dmg_used_size-OSX_inst_base_dmg_size) ))
	((OSX_inst_img_rw_size+=OSX_inst_img_rw_size/10)) # add 10% for overhead, no need to be precise
	((OSX_inst_img_rw_size=(OSX_inst_img_rw_size/512 + 1)*512)) # round to sector bound
	stage_end_ok "$OSX_inst_img_rw_size ($((OSX_inst_img_rw_size/(1024*1024))) MiB)"
fi

stage_start "Checking for available disk space"
unset tmp_dir_free_space || exit_with_error
tmp_dir_free_space="$(df -bi "$tmp_dir" | \
	sed -nE -e 's|^.+[[:space:]]+[0-9]+[[:space:]]+[0-9]+[[:space:]]+([0-9]+)[[:space:]]+[0-9]{1,3}%[[:space:]]+[0-9]+[[:space:]]+[0-9]+[[:space:]]+[0-9]{1,3}%[[:space:]]+/.*$|\1|p' )" || unset tmp_dir_free_space
if [[ "${tmp_dir_free_space-notset}" == "notset" ]] || ( [[ -n "$tmp_dir_free_space" ]] && !((tmp_dir_free_space)) ); then
	tmp_dir_free_space='0'
	stage_end_warn "Can't determinate"
else
	((tmp_dir_free_space*=512))
	if ((tmp_dir_free_space < OSX_inst_img_rw_size)); then
		stage_end_warn "$tmp_dir_free_space ($((tmp_dir_free_space/(1024*1024))) MiB), image creation may fail"
	else
		stage_end_ok "$tmp_dir_free_space ($((tmp_dir_free_space/(1024*1024))) MiB)"
	fi
fi

stage_start "Checking for super user rights"
unset have_su_rights use_sudo sudo_prf || exit_with_error "Can't unset variables"
if [[ `id -u` != '0' ]]; then
	have_su_rights='no'
else
	have_su_rights='yes'
fi
if [[ "$have_su_rights" == "yes" ]] || [[ "$allow_sudo" != "yes" ]]; then
	use_sudo='no'
	sudo_prf=''
else
	use_sudo='yes'
	sudo_prf='sudo'
fi
if [[ "$have_su_rights" == "yes" ]]; then
	stage_end_ok 'Owned'
else
	stage_end_warn "Not owned"
fi

stage_start "Choosing creation method"
if [[ -n "$cr_method" ]]; then
	stage_end_ok "Method ${cr_method#method}, specified on command line"
	if [[ "$cr_method" != "method3" ]] && [[ "$have_su_rights" != "yes" ]] && [[ "$allow_sudo" != "yes" ]]; then
		echo_warning "Resulting image probably will be unbootable as method ${cr_method#method} require super user rights and sudo was disabled by command line"
	fi
elif [[ "$have_su_rights" != 'yes' ]]; then
	cr_method="method3"
	stage_end_ok "Method 3 as safest without super user right"
elif ((tmp_dir_free_space < OSX_inst_img_rw_size*3)); then
	cr_method="method1"
	stage_end_ok "Method 1 due to limited disk space"
else
	cr_method="method2"
	stage_end_ok "Method 2"
fi

unset img_bootable || exit_with_error
if [[ "$cr_method" == "method1" ]] || [[ "$cr_method" == "method2" ]]; then
	if [[ "$cr_method" == "method1" ]]; then
		stage_start_nl "Converting BaseSystem.dmg to writable image"
		OSX_inst_img_rw="$tmp_dir/OS_X_Install.sparsebundle"
		hdiutil convert "$OSX_inst_base_dmg" -format UDSB -o "$OSX_inst_img_rw" -pmap || exit_with_error "Can't convert to writable image"
		stage_end_ok "Converting succeed"
	elif [[ "$cr_method" == "method2" ]]; then
		stage_start_nl "Creating installation image from BaseSystem.dmg"
		OSX_inst_img_dmg_tmp="$tmp_dir/OS_X_Install.dmg" || exit_with_error
		hdiutil create  "${OSX_inst_img_dmg_tmp}" -srcdevice "$OSX_inst_base_dmg" -layout ISOCD || exit_with_error "Can't create writable image"
		stage_end_ok "Creating succeed"

		stage_start_nl "Converting installation image to writeable format"
		OSX_inst_img_rw="$tmp_dir/OS_X_Install.sparsebundle"
		hdiutil convert "$OSX_inst_img_dmg_tmp" -format UDSB -o "$OSX_inst_img_rw" -pmap || exit_with_error "Can't convert to writable image"
		rm -f "$OSX_inst_img_dmg_tmp"
		stage_end_ok "Converting succeed"
	fi

	stage_start "Resizing writable image"
	hdiutil resize -size "$OSX_inst_img_rw_size" "$OSX_inst_img_rw" -nofinalgap || exit_with_error "Can't resize writable image"
	stage_end_ok "Resizing succeed"

	stage_start_nl "Mounting writable image"
	OSX_inst_img_rw_mnt="$tmp_dir/OS_X_Install_img_rw_mnt"
	hdiutil attach "$OSX_inst_img_rw" -readwrite -nobrowse -mountpoint "$OSX_inst_img_rw_mnt" ${ver_opt+-noverify} -owners on || exit_with_error "Can't mount writable image"
	stage_end_ok "Mounting succeed"
elif [[ "$cr_method" == "method3" ]]; then
	stage_start_nl "Creating blank writable image"
	OSX_inst_img_rw="$tmp_dir/OS_X_Install.sparsebundle"
	OSX_inst_img_rw_tmp_name="$OSX_inst_prt_name" || exit_with_error
	hdiutil create -size "$OSX_inst_img_rw_size" "$OSX_inst_img_rw" -type SPARSEBUNDLE -fs HFS+ -layout ISOCD -volname "$OSX_inst_img_rw_tmp_name" || exit_with_error "Can't create writable image"
	stage_end_ok "Creating succeed"

	stage_start_nl "Mounting writable image"
	OSX_inst_img_rw_mnt="$tmp_dir/OS_X_Install_img_rw_mnt"
	hdiutil attach "$OSX_inst_img_rw" -readwrite -nobrowse -mountpoint "$OSX_inst_img_rw_mnt" ${ver_opt+-noverify} || exit_with_error "Can't mount writable image"
	stage_end_ok "Mounting succeed"

	stage_start "Detecting mounted image device node"
	OSX_inst_img_rw_dev=`diskutil info -plist "$OSX_inst_img_rw_mnt" | sed -n -e '\|<key>DeviceIdentifier</key>| { N; s|^.*<string>\(.\{1,\}\)</string>.*$|/dev/\1|p; q; }'` && \
		[[ -n "$OSX_inst_img_rw_dev" ]] || exit_with_error "Can't find device node"
	stage_end_ok "$OSX_inst_img_rw_dev"

	stage_start_nl "Restoring BaseSystem.dmg to writable image"
	asr restore --source "$OSX_inst_base_dmg" --target "$OSX_inst_img_rw_dev" --erase --noprompt $ver_opt --buffers 1 --buffersize 64m || exit_with_error "Can't restore BaseSystem.dmg to writable image"
	unset OSX_inst_img_rw_mnt || exit_with_error # OSX_inst_img_rw_mnt is no valid anymore as image was remounted to different mountpoint
	img_bootable='yes'
	stage_end_ok "Restoring succeed"

	stage_start "Detecting re-mounted image volume name"
	unset OSX_inst_img_rw_volname || exit_with_error
	OSX_inst_img_rw_volname=`diskutil info -plist "$OSX_inst_img_rw_dev" | sed -n -e '\|<key>VolumeName</key>| { N; s|^.*<string>\(.\{1,\}\)</string>.*$|\1|p; q; }'` || unset OSX_inst_img_rw_folname
	if [[ -z "$OSX_inst_img_rw_volname" ]]; then
		stage_end_warn "can't detect"
	else
		osascript -e "Tell application \"Finder\" to close the window \"$OSX_inst_img_rw_volname\"" &>/dev/null
		stage_end_ok "$OSX_inst_img_rw_volname"
	fi

	stage_start_nl "Remounting writable image to predefined mountpoint"
	hdiutil detach "$OSX_inst_img_rw_dev" -force || exit_with_error "Can't unmount image"
	unset OSX_inst_img_rw_dev
	OSX_inst_img_rw_mnt="$tmp_dir/OS_X_Install_img_rw_mnt"
	hdiutil attach "$OSX_inst_img_rw" -readwrite -nobrowse -mountpoint "$OSX_inst_img_rw_mnt" ${ver_opt+-noverify} || exit_with_error "Can't mount writable image"
	stage_end_ok "Remounting succeed"
else
	exit_with_error "Unknown creation method"
fi

custom_boot_plist=
if [[ -f "$script_dir/org.chameleon.Boot.plist" ]] ; then
    custom_boot_plist="$script_dir/org.chameleon.Boot.plist"
fi
if [[ -f "$work_dir/org.chameleon.Boot.plist" ]] ; then
    custom_boot_plist="$work_dir/org.chameleon.Boot.plist"
fi
if [[ -n "$custom_boot_plist" ]] ; then
    stage_start "Installing custom boot.plist"
    mkdir $OSX_inst_img_rw_mnt/Extra
    cp "$custom_boot_plist" "$OSX_inst_img_rw_mnt/Extra/org.chameleon.Boot.plist"
    stage_end_ok "done"
fi

stage_start "Detecting macOS version on image"
unset OSX_inst_ver || exit_with_error "Can't unset variable"
OSX_inst_img_rw_ver_file="$OSX_inst_img_rw_mnt/System/Library/CoreServices/SystemVersion.plist" || exit_with_error "Can't set variable"
OSX_inst_ver=`sed -n -e '\|<key>ProductUserVisibleVersion</key>| { N; s|^.*<string>\(.\{1,\}\)</string>.*$|\1|p; q; }' "$OSX_inst_img_rw_ver_file"` || unset OSX_inst_ver
if [[ -z "$OSX_inst_ver" ]]; then
	stage_end_warn "not detected"
else
	stage_end_ok "$OSX_inst_ver"
fi

[[ "$OSX_inst_ver" =~ ^10.11($|.[1-4]$)|^10.12($|.[1-5]$) ]] || \
	echo_warning "Warning! This script is tested only with images of macOS versions 10.11.0-10.11.4 and 10.12.0-10.12.5. Use with your own risk!"

stage_start_nl "Renaming partition on writeable image"
if ! diskutil rename "$OSX_inst_img_rw_mnt" "$OSX_inst_prt_name"; then
	stage_end_warn "Partition was not renamed"
else
	unset OSX_inst_img_rw_volname
	stage_end_ok "Renamed to \"$OSX_inst_prt_name\""
fi

stage_start "Copying BaseSystem.dmg to writeable image"
cp -p "$OSX_inst_base_dmg" "$OSX_inst_img_rw_mnt/" || exit_with_error "Copying BaseSystem.dmg failed"
cp -p "${OSX_inst_base_dmg%.dmg}.chunklist" "$OSX_inst_img_rw_mnt/" || exit_with_error "Copying BaseSystem.chunklist failed"
stage_end_ok

stage_start "Extracting kernel from Essentials.pkg (very slow step)"
cd "$OSX_inst_img_rw_mnt"
# "$script_dir/pbzx" "$OSX_inst_inst_dmg_mnt/Packages/Essentials.pkg" | cpio -idmu ./System/Library/Kernels || exit_with_error "Extraction of kernel failed"
tar -xOf "$OSX_inst_inst_dmg_mnt/Packages/Essentials.pkg" Payload | python "$script_dir/parse_pbzx.py" | cpio -idmu ./System/Library/Kernels || exit_with_error "Extraction of kernel failed"
cd "$work_dir"
stage_end_ok

# Inject kext(s) into ISO image
if [[ "$inject_kexts" == "yes" ]]; then
	stage_start "Injecting kext(s) into ISO image (unsupported)"
	cd "$OSX_inst_img_rw_mnt"

	kext_name="QemuUSBTablet1011.kext"
	cp -a "$script_dir/kexts/$kext_name" ./System/Library/Extensions/
	chmod -R 755 ./System/Library/Extensions/$kext_name
	chown -R root:wheel ./System/Library/Extensions/$kext_name

	kext_name="FakeSMC.kext"
	cp -a "$script_dir/kexts/$kext_name" ./System/Library/Extensions/
	chmod -R 755 ./System/Library/Extensions/$kext_name
	chown -R root:wheel ./System/Library/Extensions/$kext_name

	touch ./System/Library/Extensions
	cd "$work_dir"
	stage_end_ok
fi

stage_start "Replacing Packages symlink with real files"
rm -f "$OSX_inst_img_rw_mnt/System/Installation/Packages" || exit_with_error "Deleting Packages symlink failed"
cp -pPR "$OSX_inst_inst_dmg_mnt/Packages" "$OSX_inst_img_rw_mnt/System/Installation/" || exit_with_error "Copying Packages failed"
stage_end_ok

stage_start "Configuring image as bootable"
OSX_inst_img_rw_CoreSrv="$OSX_inst_img_rw_mnt/System/Library/CoreServices" || exit_with_error
if bless --folder "$OSX_inst_img_rw_CoreSrv" \
	--file "$OSX_inst_img_rw_CoreSrv/boot.efi" --openfolder "$OSX_inst_img_rw_mnt" --label "Install $OSX_inst_name"; then
	stage_end_ok
else
	stage_end_warn "Failed, image may not be bootable"
fi

stage_start_nl "Unmounting InstallESD.dmg"
hdiutil detach "$OSX_inst_inst_dmg_mnt" -force || exit_with_error "Can't unmount InstallESD.dmg"
unset OSX_inst_img_rw_dev
stage_end_ok "Unmounting succeed"

stage_start_nl "Unmounting writable images"
hdiutil detach "$OSX_inst_img_rw_mnt" -force || exit_with_error "Can't unmount writable image"
unset OSX_inst_img_rw_dev
stage_end_ok "Unmounting succeed"

insert_version_into_name() {
	local name="$1"
	local version="$2"
	[[ -z "$name" ]] && return 1
	[[ -z "$version" ]] && { echo "$name"; return 0; }
	local result
	local ins_aft
	if [[ "$name" =~ (^|[[:space:]])"OS X"($|[[:space:]]) ]]; then
		ins_aft="OS X"
	elif [[ "$name" =~ (^|[[:space:]])"MacOS X"($|[[:space:]]) ]]; then
		ins_aft="MacOS X"
	elif [[ "$name" =~ (^|[[:space:]])"macOS"($|[[:space:]]) ]]; then
		ins_aft="macOS"
	fi
	if [[ -n "$ins_aft" ]]; then
		result=$(echo -n "$name" | sed -n -e 's|^\(.*[[:<:]]'"$ins_aft"'[[:>:]]\).*$|\1|p') || return 2
		[[ -z "$result" ]] && return 2
		result+=" $version" # allow any regex/special symbols in $version
		result+=$(echo -n "$name" | sed -n -e 's|^.*[[:<:]]'"$ins_aft"'[[:>:]]\(.*\)$|\1|p') || return 2
	else
		result="$name (macOS $version)"
	fi
	[[ -z "$result" ]] && return 1
	echo "$result"
	return 0
}

stage_start "Checking for output directory and image name"
unset iso_name out_dir test_name || exit_with_error
if [[ -z "$cmd_par_iso" ]]; then
	iso_name="$(insert_version_into_name "$OSX_inst_name" "$OSX_inst_ver")" || exit_with_error "Script internal error"
	iso_name="Install_${iso_name// /_}.iso"
	if [[ -z "$work_dir" ]] || [[ ! -w "$work_dir/" ]]; then
		[[ -n "$HOME" ]] &&	out_dir="$HOME/Desktop" # use Desktop as fallback
		if [[ -z "$out_dir" ]] || [[ ! -w "$out_dir/" ]]; then
			# use script location directory as fallback
			script_path="$(dirname "${BASH_SOURCE[0]}" 2>/dev/null)"
			[[ -n "$script_path" ]] || script_path="${0%/*}"
			[[ -n "$script_path" ]] && out_dir="$(cd "$script_path"2 2>/dev/null && pwd)"
		fi
		[[ -n "$out_dir" ]] && [[ -w "$out_dir/" ]] || out_dir="${0%/*}"
		[[ -n "$out_dir" ]] && [[ -w "$out_dir/" ]] || exit_with_error "Can't find writable output directory"
		stage_end_warn "Directory \"$work_dir\" seems to be unwritable, \"$out_dir/$iso_name\" will be used for output"
	else
		out_dir="$work_dir"
		stage_end_ok "$work_dir/$iso_name"
	fi
else
	test_name="${cmd_par_iso}"
	[[ "${test_name:0:1}" == "/" ]] || test_name="$work_dir/$test_name"
	if [[ -d "$test_name" ]] || [[ "${test_name%/}" != "${test_name}" ]]; then
		# cmd_par_iso is output directory without filename
		out_dir="${cmd_par_iso%/}"
	else
		iso_name="${cmd_par_iso##*/}"
		if [[ "$iso_name" == "$cmd_par_iso" ]]; then
			out_dir="$work_dir"
		else
			out_dir="${cmd_par_iso%/*}"
		fi
	fi

	if [[ -z "$iso_name" ]]; then
		iso_name="$(insert_version_into_name "$OSX_inst_name" "$OSX_inst_ver")" || exit_with_error "Script internal error"
		iso_name="Install_${OSX_inst_name// /_}.iso"
	fi
	iso_name="${iso_name%.iso}.iso"

	[[ "${out_dir:0:1}" == "/" ]] || [[ -z "$out_dir" ]] || out_dir="$work_dir/${out_dir}" # relative path
	[[ -d "$out_dir/" ]] || mkdir "$out_dir/" || exit_with_error "Can't create specified output directory."
	unset test_name || exit_with_error
	test_name="$(cd "$out_dir/" 2>/dev/null && pwd)"
	[[ -n "$test_name" ]] && out_dir="$test_name" # replace with absolute path if possible
	stage_end_ok "specified on command line: \"$out_dir/$iso_name\""
fi

stage_start_nl "Converting writeable image to .iso"
unset iso_created || exit_with_error
OSX_inst_result_image_ro="$out_dir/$iso_name" || exit_with_error
OSX_inst_result_flag="$tmp_dir/output_image_is_ready" || exit_with_error
rm -f "$OSX_inst_result_flag" || exit_with_error
[[ -e "$OSX_inst_result_image_ro" ]] && exit_with_error "\"$OSX_inst_result_image_ro\" already exist"
makehybrid_errout="$tmp_dir/hdiutil_makehybrid_erroutput" || exit_with_error
{ { hdiutil makehybrid -o "$OSX_inst_result_image_ro" "$OSX_inst_img_rw" -hfs -udf -default-volume-name "$OSX_inst_prt_name" 2>&1 1>&3 && \
	touch "$OSX_inst_result_flag"; } | tee "$makehybrid_errout"; } 3>&1 1>&2 # output stderr to stderr and save it to file at the same time
if ! [[ -e "$OSX_inst_result_flag" ]]; then
	if fgrep -Fiqs -e 'Operation not permitted' "$makehybrid_errout" && [[ "$have_su_rights" != "yes" ]]; then
		echo_warning "Creation of optimal .iso image failed without super user rights."
		if [[ "$allow_sudo" == "yes" ]]; then
			rm -f "$OSX_inst_result_image_ro"
			echo_warning "Next command will be executed with sudo, you may be asked for password."
			$sudo_prf hdiutil makehybrid -o "$OSX_inst_result_image_ro" "$OSX_inst_img_rw" -hfs -udf -default-volume-name "$OSX_inst_prt_name" && touch "$OSX_inst_result_flag"
		else
			echo_warning "Usage of sudo was disabled by command parameter"
		fi
	fi
fi
if [[ -e "$OSX_inst_result_flag" ]]; then
	img_bootable='yes'
	stage_end_ok "Converting succeed"
else
	rm -f "$OSX_inst_result_image_ro"
	stage_end_warn "Creation of optimal .iso was failed, will try to use workarounds to build usable .iso"
	[[ "$img_bootable" != 'yes' ]] && echo_warning "Resulting image may not be bootable"

	stage_start "Shrinking image"
	if hdiutil resize -sectors min "$OSX_inst_img_rw" -nofinalgap; then
		stage_end_ok "succeed"
	else
		stage_end_warn "failed, image remains larger than required"
	fi

	stage_start_nl "Converting image to .iso-like format"
	OSX_inst_result_tmp_image="${OSX_inst_result_image_ro%.iso}.cdr" || exit_with_error
	[[ -e "$OSX_inst_result_tmp_image" ]] && OSX_inst_result_tmp_image="$tmp_dir/tmp_cdr_img.cdr"
	hdiutil convert "$OSX_inst_img_rw" -format UDTO -o "$OSX_inst_result_tmp_image" && \
		mv -vn "$OSX_inst_result_tmp_image" "$OSX_inst_result_image_ro" && iso_created='yes'
	if [[ "$iso_created" != "yes" ]]; then
		rm -f "$OSX_inst_result_tmp_image"
		rm -f "$OSX_inst_result_image_ro"
		exit_with_error "Image converting failed"
	fi
	stage_end_ok "Converting succeed"
fi

echo_enh "
Resulting .iso location:"
echo "$OSX_inst_result_image_ro
"
[[ "$img_bootable" != 'yes' ]] && echo_warning "Resulting .iso may not be bootable"
