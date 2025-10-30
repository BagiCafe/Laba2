import tarfile
from pathlib import Path


def tar_command(args: str, current_catalog: str, get_absolute_path, parse_args) -> str:
    try:
        flags, parameters = parse_args(args)  # Разбираем аргументы на флаги и параметры

        if len(parameters) < 2:
            return "ERROR: Необходимо указать каталог и имя архива"

        # Получаем абсолютные пути для каталога и архива
        catalog = get_absolute_path(parameters[0], current_catalog)
        archive = get_absolute_path(parameters[1], current_catalog)

        # Создаем объекты Path для удобной работы с путями
        catalog_path = Path(catalog)
        archive_path = Path(archive)

        if not catalog_path.exists():
            return f"ERROR: Каталог не существует: {catalog}"

        if not catalog_path.is_dir():
            return f"ERROR: Не является каталогом: {catalog}"

        if archive_path.suffixes != ['.tar', '.gz']:
            return "ERROR: Архив должен иметь расширение .tar.gz"

        try:
            with tarfile.open(archive_path, 'w:gz') as tar_file:  # Создаем TAR.GZ архив в режиме записи
                for file_path in catalog_path.rglob('*'):  # Рекурсивно обходим все файлы и подкаталоги в целевом каталоге
                    if file_path == archive_path:
                        continue

                    relative_path = file_path.relative_to(catalog_path)  # Вычисляем относительный путь для сохранения в архиве

                    tar_file.add(file_path, relative_path)

            return f"TAR.GZ архив создан: {catalog} -> {archive}"

        except Exception as e:
            return f"ERROR: Ошибка создания архива: {str(e)}"

    except Exception as e:
        return f"ERROR: {str(e)}"