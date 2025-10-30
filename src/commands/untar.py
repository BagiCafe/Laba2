import tarfile
from pathlib import Path


def untar_command(args: str, current_catalog: str, get_absolute_path, parse_args) -> str:
    try:
        flags, parameters = parse_args(args)  # Разбираем аргументы на флаги и параметры

        if not parameters:
            return "ERROR: Не указан архив для распаковки"

        archive = get_absolute_path(parameters[0], current_catalog)  # Получаем абсолютный путь к архиву

        if len(parameters) > 1:  # Если указан целевой каталог, используем его, иначе распаковываем в текущий
            catalog = get_absolute_path(parameters[1], current_catalog)
        else:
            catalog = current_catalog

        # Создаем объекты Path для удобной работы с путями
        archive_path = Path(archive)
        catalog_path = Path(catalog)

        if not archive_path.exists():
            return f"ERROR: Архив не существует: {archive}"

        if not archive_path.is_file():
            return f"ERROR: Не является файлом: {archive}"

        if archive_path.suffixes != ['.tar', '.gz']:
            return "ERROR: Файл не является TAR.GZ архивом (должен иметь расширение .tar.gz)"

        if not catalog_path.exists():
            try:
                catalog_path.mkdir(parents=True, exist_ok=True)  # Создаем целевой каталог, включая все промежуточные каталоги
            except Exception as e:
                return f"ERROR: Не удалось создать целевой каталог: {str(e)}"

        if not catalog_path.is_dir():
            return f"ERROR: Цель не является каталогом: {catalog}"

        try:
            with tarfile.open(archive, 'r:gz') as tar:  # Открываем tar.gz архив в режиме чтения
                tar.extractall(catalog_path)  # Извлекаем все файлы из архива в целевой каталог

            return f"TAR.GZ архив распакован: {archive} -> {catalog}"

        except tarfile.ReadError:
            return "ERROR: Архив поврежден или не является корректным TAR.GZ файлом"

        except Exception as e:
            return f"ERROR: Ошибка распаковки архива: {str(e)}"

    except Exception as e:
        return f"ERROR: {str(e)}"