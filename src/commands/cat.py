from pathlib import Path


def cat_command(args: str, current_catalog: str, get_absolute_path, parse_args) -> str:
    try:
        flags, parameters = parse_args(args)  # Разбираем аргументы на флаги и параметры

        if not parameters:
            return "ERROR: Не указан файл"

        file_path = get_absolute_path(parameters[0], current_catalog)  # Получаем абсолютный путь к указанному файлу
        path_object = Path(file_path)  # Создаем объект Path для удобной работы с путем

        if not path_object.exists():
            return f"ERROR: Файл не существует: {file_path}"

        if path_object.is_dir():
            return f"ERROR: Является каталогом: {file_path}"

        try:
            with open(file_path, 'r', encoding='utf-8') as f:  # Открываем файл в режиме чтения с кодировкой utf-8
                content = f.read()
            return content
        except UnicodeDecodeError: # Если файл бинарный или имеет другую кодировку, которую нельзя прочитать как текст
            return "ERROR: Не удается прочитать файл "

    except Exception as e:
        return f"ERROR: {str(e)}"