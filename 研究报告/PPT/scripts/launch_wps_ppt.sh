#!/bin/bash
set -eu
export DISPLAY=:139
export XDG_CONFIG_HOME=/tmp/xuzhou-ppt-wps/config
export XDG_CACHE_HOME=/tmp/xuzhou-ppt-wps/cache
export XDG_DATA_HOME=/tmp/xuzhou-ppt-wps/data
export XDG_RUNTIME_DIR=/tmp/xuzhou-ppt-wps/runtime
export TMPDIR=/tmp/xuzhou-ppt-wps/tmp
export LANG=zh_CN.UTF-8
export LANGUAGE=zh_CN
export LC_ALL=zh_CN.UTF-8
export QT_X11_NO_MITSHM=1
export QT_XCB_GL_INTEGRATION=none
mkdir -p "$XDG_CONFIG_HOME" "$XDG_CACHE_HOME" "$XDG_DATA_HOME" "$XDG_RUNTIME_DIR" "$TMPDIR"
chmod 700 "$XDG_RUNTIME_DIR"
if [ ! -e "$XDG_DATA_HOME/fonts" ]; then
  ln -s /home/xh/.local/share/fonts "$XDG_DATA_HOME/fonts"
fi
unset SESSION_MANAGER DBUS_SESSION_BUS_ADDRESS
exec dbus-run-session -- /opt/kingsoft/wps-office/office6/wpsoffice /prometheus /tmp/xuzhou-report-ppt-draft.pptx
