import os
import stat
import operator
from pathlib import Path
from datetime import datetime


def file_info(file_path: Path) -> str:  # Получаем подробную информацию о файле
    try:
        stat_info = file_path.stat()  # Получаем статистику каталога/файла
        permissions = stat.filemode(stat_info.st_mode)  # Получаем права доступа в формате rwxrwxrwx
        size = stat_info.st_size  # Размер файла в байтах
        time = datetime.fromtimestamp(stat_info.st_mtime).strftime('%Y-%m-%d %H:%M')  # Время последней модификации
        name = file_path.name  # Обработка имени файла

        if file_path.is_symlink():  # Для символических ссылок показываем куда они ведут
            try:
                target_path = os.readlink(file_path)
                name = f"{file_path.name} -> {target_path}"
            except OSError:  # Если ссылка битая
                name = f"{file_path.name} -> [broken]"

        return f"{permissions} {stat_info.st_nlink:>2} {size:>8} {time} {name}"  # Форматируем строку вывода
    except Exception:
        return f"?????????? {'?':>2} {'?':>8} {file_path.name}"  # Если не удалось получить информацию о файле


def files_list(target_path: Path) -> list:  # Получаем список файлов в указанном пути
    if target_path.is_file():  # Определяем файл это или каталог
        files = [target_path]
    else:
        files = [f for f in target_path.iterdir()]
    return files


def simple_output(files) -> str:  # Форматируем простой вывод (без флага -l)
    return "  ".join(f.name for f in files)


def detailed_output(files) -> str:  # Форматируем подробный вывод (с флагом -l)
    lines = []
    for file in files:
        lines.append(file_info(file))
    return "\n".join(lines)


def process_arguments(args: str, current_catalog: str, get_absolute_path, parse_args) -> tuple:  #Обрабатываем аргументы команды и определяем целевой путь
    flags, parameters = parse_args(args)
    if parameters: target0 = parameters[0]
    else: target0 = current_catalog
    path = get_absolute_path(target0, current_catalog)  # Получаем абсолютный путь к целевому каталогу/файлу
    target_path = Path(path)  # Создаем объект Path для работы с путями
    return target_path, flags, parameters


def ls_command(args: str, current_catalog: str, get_absolute_path, parse_args) -> str:
    try:
        target, flags, parameters = process_arguments(args, current_catalog, get_absolute_path, parse_args)  # Обрабатываем аргументы и получаем целевой путь
        if not target.exists():
            return "ERROR: Такого файла или каталога нет"
        files = files_list(target)
        files.sort(key=operator.attrgetter('name'))  # Сортируем файлы по имени для стандартного формата
        if '-l' not in flags:
            return simple_output(files)
        else:
            return detailed_output(files)
    except PermissionError as e:
        return f"ERROR: Ошибка прав доступа: {str(e)}"
    except Exception as e:
        return f"ERROR: {str(e)}"