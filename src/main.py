import os
import sys
import logging
from pathlib import Path


sys.path.append(os.path.join(os.path.dirname(__file__), 'commands'))  # Добавляем путь к командам в sys.path для импорта модулей из папки commands


from commands.ls import ls_command
from commands.cd import cd_command
from commands.cat import cat_command
from commands.cp import cp_command
from commands.mv import mv_command
from commands.rm import rm_command
from commands.zip import zip_command
from commands.unzip import unzip_command
from commands.tar import tar_command
from commands.untar import untar_command
from commands.grep import grep_command


def setup_logging():  # Настройка логирования в файле shell.log
    log_file = "shell.log"
    logging.basicConfig(
        filename=log_file,
        level=logging.INFO,
        format='[%(asctime)s] %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )


def log_command(command: str, flag=True , error_message=""):
    # Определяем статус выполнения
    if flag: status = "SUCCESS"
    else: status = f"ERROR: {error_message}"
    log_message = f"{command} - {status}"  # Формируем строку для лога
    logging.info(log_message)  # Записываем в файл лога
    print(log_message)


def get_absolute_path(path: str, current_catalog: str) -> str:  # Преобразование относительного пути в абсолютный
    if not path:
        return current_catalog
    path_object = Path(path)  # Создаем объект Path для работы с путями
    if path_object.is_absolute():
        return str(path_object)
    else:
        return str(Path(current_catalog) / path)  # Объединяем с текущим каталогом


def parse_args(args_str: str) -> tuple:  # Разбор строки аргументов на флаги и параметры
    if not args_str:
        return [], []
    args = args_str.split()
    flags = [arg for arg in args if arg.startswith('-')]
    parameters = [arg for arg in args if not arg.startswith('-')]
    return (flags, parameters)


def main():
    setup_logging()  # Настраиваем логирование
    current_catalog = os.getcwd()  # Получаем текущий рабочий каталог

    print("Текущий католог:", current_catalog)

    while True:
        try:
            prompt = f"\n{current_catalog}> "
            user_input = input(prompt).strip()

            if not user_input:  # Пропускаем пустые вводы
                continue

            parts = user_input.split(maxsplit=1)  # Разбиваем на 2 части: команда и остальное
            command = parts[0]
            if len(parts) > 1: args = parts[1]
            else: args = ""

            result = ""
            flag = True
            error_message = ""

            try:
                if command == 'ls':
                    result = ls_command(args, current_catalog, get_absolute_path, parse_args)
                elif command == 'cd':
                    new_current = cd_command(args, current_catalog, get_absolute_path, parse_args)
                    if new_current:  # Если команда cd вернула новый каталог
                        current_catalog = new_current  # Обновляем текущий каталог
                        result = f"Текущий каталог: {current_catalog}"
                elif command == 'cat':
                    result = cat_command(args, current_catalog, get_absolute_path, parse_args)
                elif command == 'cp':
                    result = cp_command(args, current_catalog, get_absolute_path, parse_args)
                elif command == 'mv':
                    result = mv_command(args, current_catalog, get_absolute_path, parse_args)
                elif command == 'rm':
                    result = rm_command(args, current_catalog, get_absolute_path, parse_args)
                elif command == 'zip':
                    result = zip_command(args, current_catalog, get_absolute_path, parse_args)
                elif command == 'unzip':
                    result = unzip_command(args, current_catalog, get_absolute_path, parse_args)
                elif command == 'tar':
                    result = tar_command(args, current_catalog, get_absolute_path, parse_args)
                elif command == 'untar':
                    result = untar_command(args, current_catalog, get_absolute_path, parse_args)
                elif command == 'grep':
                    result = grep_command(args, current_catalog, get_absolute_path, parse_args)
                else:
                    result = f"Неизвестная команда: {command}"
                    flag = False
                    error_message = f"Unknown command: {command}"

            except Exception as e:
                result = f"ERROR: {str(e)}"
                flag = False
                error_message = str(e)

            if result:
                print(result)

            log_command(user_input, flag, error_message)  # Логирование выполненной команды

        except KeyboardInterrupt:
            break
        except Exception as e:
            print(f"Критическая ошибка: {e}")
            log_command("system", False, f"Critical error: {e}")


if __name__ == "__main__":
    main()