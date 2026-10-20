#!/bin/bash
set -eu
# Run only through unshare --user --map-root-user --mount. Mount changes stay local.
mount --make-rprivate /
mount --bind /tmp/xuzhou-ppt-wps/no-addins /home/xh/.local/share/Kingsoft/wps/jsaddons
exec bash "$(dirname "$0")/launch_wps_ppt.sh"
