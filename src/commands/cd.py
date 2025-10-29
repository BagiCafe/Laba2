from pathlib import Path


def cd_command(args: str, current_catalog: str, get_absolute_path, parse_args) -> str:
    try:
        flags, parameters = parse_args(args)  # Разбираем аргументы на флаги и параметры

        if not parameters:
            home_catalog = Path.home()
            return str(home_catalog)  # Возвращаем абсолютный путь домашнего каталога

        path = parameters[0] # Берем первый параметр как целевой путь

        # Обрабатываем специальные символы и пути
        if path == "~":
            home_catalog = Path.home()  # домашний каталог пользователя
            return str(home_catalog)
        elif path == "..":
            new_catalog = Path(current_catalog).parent  # переход на родительский каталог
            return str(new_catalog)
        elif path == "-":
            return current_catalog  # возвращаем текущий каталог

        new_catalog = get_absolute_path(path, current_catalog)  # Преобразуем относительный путь в абсолютный относительно текущего каталога
        path_object = Path(new_catalog)  # Создаем объект Path для проверки существования и типа

        if not path_object.exists():
            return f"ERROR: Каталог не существует: {new_catalog}"

        if not path_object.is_dir():
            return f"ERROR: Не является каталогом: {new_catalog}"

        return new_catalog  # Возвращаем новую директорию

    except Exception as e:
        return f"ERROR: {str(e)}"