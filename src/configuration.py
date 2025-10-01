import yaml

class ShellConfig:
    """
    Класс для хранения конфигурации эмулятора
    """

    def __init__(self):
        self.vfs_path = None
        self.startup_script = None
        self.config_file = None

    def dump(self):
        """
        Вывод конфигурации в формате ключ-значение
        """
        config_data = {
            "vfs_path": self.vfs_path,
            "startup_script": self.startup_script,
            "config_file": self.config_file
        }
        for key, value in config_data.items():
            print(f"{key}: {value}")

def load_config_file(config_path):
    """
    Загрузка конфигурации из YAML файла
    """
    try:
        with open(config_path, 'r', encoding='utf-8') as file:
            config_data = yaml.safe_load(file)
        return config_data
    except Exception as e:
        print(f"Error reading configuration file: {e}")
        return None


def merge_configurations(cmd_args, config_file_data):
    """
    Объединение конфигураций с приоритетом файла над командной строкой
    """
    config = ShellConfig()

    # Устанавливаем значения из командной строки
    config.vfs_path = cmd_args.vfs_path
    config.startup_script = cmd_args.startup_script
    config.config_file = cmd_args.config_file

    # Перезаписываем значения из конфигурационного файла (если они есть)
    if config_file_data:
        if 'vfs_path' in config_file_data:
            config.vfs_path = config_file_data['vfs_path']
        if 'startup_script' in config_file_data:
            config.startup_script = config_file_data['startup_script']

    return config


def debug_print_config(config):
    """
    Отладочный вывод конфигурации
    """
    print("=== Shell Emulator Configuration ===")
    config.dump()
    print("====================================")