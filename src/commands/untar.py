import tarfile
from pathlib import Path


def archive_target_paths(parameters: list, current_catalog: str, get_absolute_path) -> tuple:  # Получаем абсолютные пути для архива и целевого каталога
    if not parameters:
        return "", ""
    archive = get_absolute_path(parameters[0], current_catalog)
    if len(parameters) > 1:
        catalog = get_absolute_path(parameters[1], current_catalog)
    else:
        catalog = current_catalog
    return archive, catalog


def validate_archive_path(archive_path: str) -> tuple:  #Проверяем существование и архив ли это
    archive_object = Path(archive_path)
    if not archive_object.exists():
        return False, f"ERROR: Архив не существует: {archive_path}"
    if not archive_object.is_file():
        return False, f"ERROR: Не является файлом: {archive_path}"
    return True, archive_path


def validate_archive_format(archive_path: str) -> tuple:  # Проверяем формат архива
    archive_object = Path(archive_path)
    if archive_object.suffixes != ['.tar', '.gz']:
        return False, "ERROR: Файл не является TAR архивом (должен иметь расширение .tar.gz)"
    return True, archive_path


def create_target_directory(catalog_path: str) -> tuple:  # Создаем целевой каталог, если он не существует
    catalog_object = Path(catalog_path)
    try:
        catalog_object.mkdir(parents=True, exist_ok=True)  # Создаем целевой каталог, включая все промежуточные каталоги
        return True, catalog_path
    except Exception as e:
        return False, f"ERROR: Не удалось создать целевой каталог: {str(e)}"


def validate_target_directory(catalog_path: str) -> tuple:  # Проверяем целевой каталог
    catalog_object = Path(catalog_path)
    if not catalog_object.exists():
        success, result = create_target_directory(catalog_path)
        if not success:
            return False, result
    if not catalog_object.is_dir():
        return False, f"ERROR: Цель не является каталогом: {catalog_path}"
    return True, catalog_path


def extract_tar_archive(archive_path: str, catalog_path: str) -> tuple:  # Извлекаем файлы из TAR архива
    try:
        with tarfile.open(archive_path, 'r:gz') as tar:
            tar.extractall(catalog_path) # Извлекаем все файлы из архива в целевой каталог
        return True, f"TAR архив распакован: {archive_path} -> {catalog_path}"
    except tarfile.ReadError:
        return False, "ERROR: Архив поврежден или не является корректным TAR файлом"
    except Exception as e:
        return False, f"ERROR: Ошибка распаковки архива: {str(e)}"


def untar_command(args: str, current_catalog: str, get_absolute_path, parse_args) -> str:
    try:
        flags, parameters = parse_args(args)  # Разбираем аргументы на флаги и параметры
        archive, catalog = archive_target_paths(parameters, current_catalog, get_absolute_path)
        if not archive:
            return "ERROR: Не указан архив для распаковки"
        archive_valid, archive_result = validate_archive_path(archive)
        if not archive_valid:
            return archive_result
        format_valid, format_result = validate_archive_format(archive_result)
        if not format_valid:
            return format_result
        target_valid, target_result = validate_target_directory(catalog)
        if not target_valid:
            return target_result
        success, result = extract_tar_archive(format_result, target_result)
        return result
    except PermissionError as e:
        return f"ERROR: Ошибка прав доступа: {str(e)}"
    except Exception as e:
        return f"ERROR: {str(e)}"