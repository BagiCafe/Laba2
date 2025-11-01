import shutil
from pathlib import Path


def source_purpose_paths(parameters: list, current_catalog: str, get_absolute_path) -> tuple:  # Получаем абсолютные пути для источника и назначения
    if len(parameters) < 2:
        return "", ""
    source = get_absolute_path(parameters[0], current_catalog)
    purpose = get_absolute_path(parameters[1], current_catalog)
    return source, purpose


def validate_source_path(source_path: str) -> tuple:  # Проверяем существование источника
    source_object = Path(source_path)  # Создаем объекты Path для удобной работы с путями
    if not source_object.exists():
        return False, f"ERROR: Источник не существует: {source_path}"
    return True, source_path


def copy_directory_recursive(source: str, purpose: str) -> tuple:  # Рекурсивно копируем весь каталог с содержимым
    try:
        shutil.copytree(source, purpose)
        return True, f"Каталог скопирован: {source} -> {purpose}"
    except Exception as e:
        return False, f"ERROR: Ошибка копирования каталога: {str(e)}"


def copy_file(source: str, purpose: str) -> tuple:  # Копируем файл
    try:
        shutil.copy2(source, purpose)
        return True, f"Файл скопирован: {source} -> {purpose}"
    except Exception as e:
        return False, f"ERROR: Ошибка копирования файла: {str(e)}"


def handle_directory_copy(source: str, purpose: str, recursive: bool) -> tuple:  # Обрабатываем копирование директории
    if not recursive:
        return False, "ERROR: Используйте -r для копирования каталогов"
    return copy_directory_recursive(source, purpose)


def handle_file_copy(source: str, purpose: str) -> tuple:  # Обрабатываем копирование файла
    return copy_file(source, purpose)


def cp_command(args: str, current_catalog: str, get_absolute_path, parse_args) -> str:
    try:
        flags, parameters = parse_args(args)  # Разбираем аргументы на флаги и параметры
        source, purpose = source_purpose_paths(parameters, current_catalog, get_absolute_path)
        if not source or not purpose:
            return "ERROR: Необходимо указать источник и назначение"
        valid, validation_result = validate_source_path(source)
        if not valid:
            return validation_result
        source_path = Path(source)
        purpose_path = Path(purpose)
        recursive = '-r' in flags  # Проверяем флаг рекурсивного копирования
        if source_path.is_dir():
            if recursive:
                success, result = copy_directory_recursive(source, purpose_path)
            else:
                success, result = handle_directory_copy(source, purpose_path, recursive)
        else:
            success, result = handle_file_copy(source, purpose_path)
        return result
    except Exception as e:
        return f"ERROR: {str(e)}"