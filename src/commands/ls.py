import os
import stat
import operator
from pathlib import Path
from datetime import datetime


def ls_command(args: str, current_catalog: str, get_absolute_path, parse_args) -> str:
    try:
        flags, parameters = parse_args(args)  # Разбираем аргументы на флаги и параметры
        path = get_absolute_path(parameters[0] if parameters else current_catalog, current_catalog)  # Получаем абсолютный путь к целевому каталогу/файлу
        target = Path(path)  # Создаем объект Path для работы с путями

        if not target.exists():  # Проверяем существование целевого пути
            return "ERROR: Такого файла или каталога нет"

        files = []
        if target.is_file():  # Определяем файл это или каталог
            files = [target]
        else:
            files = [f for f in target.iterdir()]

        files.sort(key=operator.attrgetter('name'))  # Сортируем файлы по имени для стандартного формата

        if '-l' not in flags:
            return "  ".join(f.name for f in files)  # Простой вывод (без флага -l)

        lines = []
        for file in files:  # Подробный вывод (с флагом -l)
            try:
                stat_info = file.stat() # Получаем статистику каталога/файла

                permissions = stat.filemode(stat_info.st_mode)  # Получаем права доступа в формате rwxrwxrwx

                size = stat_info.st_size  # Размер файла в байтах

                time = datetime.fromtimestamp(stat_info.st_mtime).strftime('%Y-%m-%d %H:%M')  # Время последней модификации

                name = file.name  # Обработка имени файла
                if file.is_symlink():  # Для символических ссылок показываем куда они ведут
                    try:
                        target_path = os.readlink(file)
                        name = f"{file.name} -> {target_path}"
                    except OSError:  # Если ссылка битая
                        name = f"{file.name} -> [broken]"

                lines.append(f"{permissions} {stat_info.st_nlink:>2} {size:>8} {time} {name}")  # Форматируем строку вывода
            except Exception as e:
                lines.append(f"?????????? {'?':>2} {'?':>8} {file.name}")  # Если не удалось получить информацию о файле

        return "\n".join(lines)

    except Exception as e:
        return f"ERROR: {str(e)}"