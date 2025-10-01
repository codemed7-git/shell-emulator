@echo off
echo === Test 1: Command line arguments only ===
python shell_emulator.py --vfs-path "/test/vfs" --startup-script "script1.txt"
pause

echo === Test 2: Config file only ===
python shell_emulator.py --config-file "config1.yaml"
pause

echo === Test 3: Mixed (command line + config file) ===
python shell_emulator.py --vfs-path "/cmd/vfs" --startup-script "cmd_script.txt" --config-file "config2.yaml"
pause

echo === Test 4: Error handling - missing config file ===
python shell_emulator.py --config-file "nonexistent.yaml"
pause

echo === Test 5: Error handling - script with syntax error ===
echo ls "unclosed_quote > error_script.txt
python shell_emulator.py --startup-script "error_script.txt"
del error_script.txt
pause