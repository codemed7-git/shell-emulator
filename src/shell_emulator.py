import argparse
import os
import shlex
from pathlib import Path

from configuration import merge_configurations, debug_print_config, load_config_file


def parse_arguments():
    """
    Парсинг аргументов командной строки
    """
    parser = argparse.ArgumentParser(description='Simple Shell Emulator')
    parser.add_argument('--vfs-path', type=str, help='Path to VFS physical location')
    parser.add_argument('--startup-script', type=str, help='Path to startup script')
    parser.add_argument('--config-file', type=str, help='Path to configuration file')

    return parser.parse_args()


def parse_input(command_string):
    """
    Парсит введенную строку, раскрывая переменные окружения.
    Возвращает список аргументов.
    Использует shlex для правильного разделения аргументов в кавычках.
    """
    try:
        # Разбиваем строку на части, учитывая кавычки
        args = shlex.split(command_string)
        # Заменяем каждую подстроку, начинающуюся с '$', на значение переменной окружения
        parsed_args = []
        for arg in args:
            '''Реализовать парсер, который поддерживает раскрытие переменных 
            окружения реальной ОС (например, $HOME).'''

            if arg.startswith('$'):
                # Если аргумент - чистая переменная (например, $HOME)
                var_name = arg[1:]
                parsed_args.append(os.getenv(var_name, arg))  # Если переменной нет, оставляем как было
            else:
                # Ищем и заменяем переменные внутри строки (например, "My path is $HOME")
                # Это простой вариант, можно улучшить с помощью регулярных выражений
                for env_var, value in os.environ.items():
                    arg = arg.replace(f'${env_var}', value)
                parsed_args.append(arg)
        return parsed_args
    except ValueError as e:
        # Ошибка парсинга (например, незакрытые кавычки)
        print(f"Syntax error: {e}")
        return None


def execute_startup_script(script_path, execute_command_func):
    """
    Выполнение стартового скрипта
    """
    try:
        with open(script_path, 'r', encoding='utf-8') as file:
            lines = file.readlines()

        print(f"=== Executing startup script: {script_path} ===")

        for line_num, line in enumerate(lines, 1):
            line = line.strip()
            if not line or line.startswith('#'):
                continue  # Пропускаем пустые строки и комментарии

            print(f"[SCRIPT:{line_num}] {get_current_prompt()}{line}")

            args = parse_input(line)
            if args is None:
                print(f"Script stopped due to syntax error at line {line_num}")
                return False

            # Для команды exit прерываем выполнение скрипта
            if args and args[0].lower() == "exit":
                print("Script execution interrupted by exit command")
                return False

            if not execute_command_func(args):
                print("Script execution interrupted")
                return False

        print("=== Startup script execution completed ===")
        return True

    except FileNotFoundError:
        print(f"Startup script not found: {script_path}")
        return False
    except Exception as e:
        print(f"Error executing startup script: {e}")
        return False


def get_current_prompt():
    """
    Формирует приглашение к вводу на основе реальных данных ОС.
    Формат: username@hostname:current_dir$
    """
    username = os.getenv('USER') or os.getenv('USERNAME')  # Для UNIX и Windows
    hostname = os.uname().nodename if hasattr(os, 'uname') else os.getenv('COMPUTERNAME', 'unknown-host')
    current_dir = Path.cwd().name  # Имя текущей директории
    # Базовый путь, для красоты можно заменить '~' если находимся в HOME
    base_path = Path.cwd()
    home_path = Path.home()
    try:
        # Пытаемся представить текущий путь относительно домашней директории
        current_dir_str = str(base_path.relative_to(home_path))
        if current_dir_str == '.':
            current_dir_str = '~'
        else:
            current_dir_str = '~/' + current_dir_str
    except ValueError:
        # Если не получилось (текущий путь не внутри HOME), показываем полный путь или его часть
        current_dir_str = base_path.name

    return f"{username}@{hostname}:{current_dir_str}$ "


def execute_command(args, config):
    """
    Выполняет встроенные команды оболочки.
    Возвращает False если нужно завершить работу (команда exit), иначе True.
    """
    if not args:
        # Пустая команда
        return True

    command_name = args[0].lower()

    if command_name == "exit":
        print("Goodbye!")
        return False

    # Реализовать команды-заглушки, которые выводят свое имя и аргументы: ls, cd.
    elif command_name == "cd":
        # Команда смены директории
        new_dir = args[1] if len(args) > 1 else os.getenv('HOME')
        try:
            os.chdir(new_dir)
        except FileNotFoundError:
            print(f"cd: no such file or directory: {new_dir}")
        except NotADirectoryError:
            print(f"cd: not a directory: {new_dir}")
        except PermissionError:
            print(f"cd: permission denied: {new_dir}")
        # Заглушка: просто меняем директорию, вывод не требуется

    elif command_name == "ls":
        # Заглушка для ls: просто выводим свои аргументы
        print(f"ls called with arguments: {args[1:]}")

    elif command_name == "conf-dump":
        # Вывод конфигурации эмулятора
        print("=== Current Shell Configuration ===")
        config.dump()
        print("===================================")

    else:
        # Любая другая команда воспринимается как заглушка
        print(f"Command not implemented: {command_name}. Arguments: {args[1:]}")

    return True


def main():
    """
    Главный цикл REPL (Read-Eval-Print Loop).
    """
    # Парсим аргументы командной строки
    cmd_args = parse_arguments()
    
    # ------------------------------------------------------------------------------------------- configuration.py -----
    # Загружаем конфигурационный файл если указан
    config_file_data = None
    if cmd_args.config_file:
        config_file_data = load_config_file(cmd_args.config_file)
        if config_file_data is None:
            print("Failed to load configuration file. Using command line arguments only.")

    # Объединяем конфигурации
    config = merge_configurations(cmd_args, config_file_data)

    # Отладочный вывод конфигурации
    debug_print_config(config)

    # Выполняем стартовый скрипт если указан
    if config.startup_script:
        # Создаем обертку для execute_command с конфигурацией
        def execute_command_wrapper(args):
            return execute_command(args, config)

        script_success = execute_startup_script(config.startup_script, execute_command_wrapper)
        if not script_success:
            print("Startup script execution failed. Starting interactive mode...")
    # ------------------------------------------------------------------------------------------------------------------

    print("Welcome to Simple Shell Emulator! Type 'exit' to quit.")
    is_running = True

    while is_running:
        try:
            # 1. Read (Чтение)
            prompt = get_current_prompt()
            user_input = input(prompt).strip()

            # Пропускаем пустые строки
            if not user_input:
                continue

            # 2. Eval (Парсинг и Выполнение)
            args = parse_input(user_input)
            if args is None:  # Если парсинг вернул ошибку
                continue

            is_running = execute_command(args, config)

        except KeyboardInterrupt:
            # Обработка Ctrl+C
            print("\nType 'exit' to quit.")
        except EOFError:
            # Обработка Ctrl+D (конец файла)
            print("\nExiting...")
            break


if __name__ == "__main__":
    main()
