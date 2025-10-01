#!/bin/bash
echo "=== Test 4: Error handling - missing config file ==="
python3 shell_emulator.py --config-file "nonexistent.yaml"