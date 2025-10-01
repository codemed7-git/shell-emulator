#!/bin/bash
echo "=== Test 5: Error handling - script with syntax error ==="
# Создаем скрипт с синтаксической ошибкой
echo 'ls "unclosed_quote' > error_script.txt
python3 shell_emulator.py --startup-script "error_script.txt"