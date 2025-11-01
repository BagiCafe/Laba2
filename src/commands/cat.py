from pathlib import Path


def get_file_path(parameters: list, current_catalog: str, get_absolute_path) -> str:  # Получаем абсолютный путь к указанному файлу
    if not parameters:
        return ""
    return get_absolute_path(parameters[0], current_catalog)


def validate_file(file: str) -> tuple:  # Проверяем существование файла и что это не директория
    path_object = Path(file)  # Создаем объект Path для удобной работы с путем
    if not path_object.exists():
        return False, f"ERROR: Файл не существует: {file}"
    if path_object.is_dir():
        return False, f"ERROR: Является каталогом: {file}"
    return True, file


def read_file(file: str) -> tuple:  # Читаем содержимое файла с обработкой ошибок кодировки
    try:
        with open(file, 'r', encoding='utf-8') as f:
            content = f.read()
        return True, content
    except UnicodeDecodeError:  # Если файл бинарный или имеет другую кодировку, которую нельзя прочитать как текст
        return False, "ERROR: Не удается прочитать файл"
    except Exception as e:
        return False, f"ERROR: {str(e)}"


def cat_command(args: str, current_catalog: str, get_absolute_path, parse_args) -> str:
    try:
        flags, parameters = parse_args(args)  # Разбираем аргументы на флаги и параметры
        file_path = get_file_path(parameters, current_catalog, get_absolute_path)
        if not file_path:
            return "ERROR: Не указан файл"
        valid, valid_result = validate_file(file_path)
        if not valid:
            return valid_result
        read_success, content = read_file(valid_result)
        if read_success:
            return content
        else:
            return content
    except PermissionError as e:
        return f"ERROR: Ошибка прав доступа: {str(e)}"
    except Exception as e:
        return f"ERROR: {str(e)}"