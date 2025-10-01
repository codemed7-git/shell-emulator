#!/bin/bash
echo "=== Test 3: Mixed (command line + config file) ==="
python3 shell_emulator.py --vfs-path "/cmd/vfs" --startup-script "cmd_script.txt" --config-file "config2.yaml"