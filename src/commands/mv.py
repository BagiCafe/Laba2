import shutil
from pathlib import Path


def source_destination_paths(parameters: list, current_catalog: str, get_absolute_path) -> tuple:  # Получаем абсолютные пути для источника и назначения
    if len(parameters) < 2:
        return "", ""
    source = get_absolute_path(parameters[0], current_catalog)
    purpose = get_absolute_path(parameters[1], current_catalog)
    return source, purpose


def validate_source_path(source_path: str) -> tuple:  # Проверяем существование источника
    source_object = Path(source_path)
    if not source_object.exists():
        return False, f"ERROR: Источник не существует: {source_path}"
    return True, source_path


def prepare_destination_path(source: str, purpose: str) -> str:  # Подготавливаем путь назначения
    source_path = Path(source)
    purpose_path = Path(purpose)

    # Если назначение существующая директория, то перемещаем источник в эту директорию
    if purpose_path.exists() and purpose_path.is_dir():
        return str(purpose_path / source_path.name)
    return purpose


def move_item(source: str, purpose: str) -> tuple:  # Перемещаем файл или каталог
    try:
        shutil.move(source, purpose)
        return True, f"Перемещено: {source} -> {purpose}"
    except Exception as e:
        return False, f"ERROR: Ошибка перемещения: {str(e)}"


def mv_command(args: str, current_catalog: str, get_absolute_path, parse_args) -> str:
    try:
        flags, parameters = parse_args(args)  # Разбираем аргументы на флаги и параметры
        source, purpose = source_destination_paths(parameters, current_catalog, get_absolute_path)
        if not source or not purpose:
            return "ERROR: Необходимо указать источник и назначение"
        valid, validation_result = validate_source_path(source)
        if not valid:
            return validation_result
        final_destination = prepare_destination_path(source, purpose)
        success, result = move_item(source, final_destination)
        return result
    except Exception as e:
        return f"ERROR: {str(e)}"