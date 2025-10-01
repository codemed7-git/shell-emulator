import os
import shlex
import sys
from pathlib import Path

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

def execute_command(args):
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

    else:
        # Любая другая команда воспринимается как заглушка
        print(f"Command not implemented: {command_name}. Arguments: {args[1:]}")

    return True

def main():
    """
    Главный цикл REPL (Read-Eval-Print Loop).
    """
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

            is_running = execute_command(args)

        except KeyboardInterrupt:
            # Обработка Ctrl+C
            print("\nType 'exit' to quit.")
        except EOFError:
            # Обработка Ctrl+D (конец файла)
            print("\nExiting...")
            break

if __name__ == "__main__":
    main()