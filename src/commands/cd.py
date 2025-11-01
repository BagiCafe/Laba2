from pathlib import Path


def special_paths(path: str, current_catalog: str) -> str:  # Обрабатываем специальные символы и пути
    if path == "~":
        home_catalog = Path.home()  # домашний каталог пользователя
        return str(home_catalog)
    elif path == "..":
        new_catalog = Path(current_catalog).parent  # переход на родительский каталог
        return str(new_catalog)
    elif path == "-":
        return current_catalog  # возвращаем текущий каталог
    else:
        return path  # обычный путь, не требующий специальной обработки


def target_path(parameters: list, current_catalog: str, get_absolute_path) -> str:  #Определяем целевой путь на основе параметров
    if not parameters:
        home_catalog = Path.home()
        return str(home_catalog)

    path = parameters[0]  # Берем первый параметр как целевой путь
    processed_path = special_paths(path, current_catalog)
    if Path(processed_path).is_absolute():
        return processed_path
    else:
        return get_absolute_path(processed_path, current_catalog)


def validate_directory(path: str) -> tuple:  # Проверяем, что путь существует и является директорией
    path_object = Path(path)  # Создаем объект Path для проверки существования и типа
    if not path_object.exists():
        return False, f"ERROR: Каталог не существует: {path}"
    if not path_object.is_dir():
        return False, f"ERROR: Не является каталогом: {path}"
    return True, path


def cd_command(args: str, current_catalog: str, get_absolute_path, parse_args) -> str:
    try:
        flags, parameters = parse_args(args)  # Разбираем аргументы на флаги и параметры
        target_path1 = target_path(parameters, current_catalog, get_absolute_path)
        valid, result = validate_directory(target_path1)

        if valid:
            return result
        else:
            return result

    except Exception as e:
        return f"ERROR: {str(e)}"