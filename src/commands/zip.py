import zipfile
from pathlib import Path


def catalog_archive_paths(parameters: list, current_catalog: str, get_absolute_path) -> tuple:  # Получаем абсолютные пути для каталога и архива
    if len(parameters) < 2:
        return "", ""
    catalog = get_absolute_path(parameters[0], current_catalog)
    archive = get_absolute_path(parameters[1], current_catalog)
    return catalog, archive


def validate_catalog_path(catalog_path: str) -> tuple:  # Проверяем существование и каталог ли это
    catalog_object = Path(catalog_path)
    if not catalog_object.exists():
        return False, f"ERROR: Каталог не существует: {catalog_path}"
    if not catalog_object.is_dir():
        return False, f"ERROR: Не является каталогом: {catalog_path}"
    return True, catalog_path


def validate_archive_extension(archive_path: str) -> tuple: # Проверяем расширение архива
    archive_object = Path(archive_path)
    if archive_object.suffix.lower() != '.zip':
        return False, "ERROR: Имя архива должно иметь расширение .zip"
    return True, archive_path


def add_files_zip(zip_file: zipfile.ZipFile, catalog_path: Path, archive_path: Path):  # Рекурсивно добавляем файлы в ZIP архив
    for file_path in catalog_path.rglob('*'):  # Рекурсивно обходим все файлы и подкаталоги в целевом каталоге
        if file_path == archive_path:
            continue
        relative_path = file_path.relative_to(catalog_path)  # Вычисляем относительный путь для сохранения в архиве
        zip_file.write(file_path, relative_path)


def create_zip_archive(catalog_path: str, archive_path: str) -> tuple:  # Создаем ZIP архив
    try:
        with zipfile.ZipFile(archive_path, 'w', zipfile.ZIP_DEFLATED) as zip_file:
            add_files_zip(zip_file, Path(catalog_path), Path(archive_path))
        return True, f"ZIP-архив создан: {catalog_path} -> {archive_path}"
    except Exception as e:
        return False, f"ERROR: Ошибка создания архива: {str(e)}"


def zip_command(args: str, current_catalog: str, get_absolute_path, parse_args) -> str:
    try:
        flags, parameters = parse_args(args)  # Разбираем аргументы на флаги и параметры
        catalog, archive = catalog_archive_paths(parameters, current_catalog, get_absolute_path)
        if not catalog or not archive:
            return "ERROR: Необходимо указать каталог и имя архива"
        catalog_valid, catalog_result = validate_catalog_path(catalog)
        if not catalog_valid:
            return catalog_result
        archive_valid, archive_result = validate_archive_extension(archive)
        if not archive_valid:
            return archive_result
        success, result = create_zip_archive(catalog_result, archive_result)
        return result
    except PermissionError as e:
        return f"ERROR: Ошибка прав доступа: {str(e)}"
    except Exception as e:
        return f"ERROR: {str(e)}"