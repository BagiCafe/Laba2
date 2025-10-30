import re
from pathlib import Path


def grep_command(args: str, current_catalog: str, get_absolute_path, parse_args) -> str:
    try:
        flags, parameters = parse_args(args)  # Разбираем аргументы на флаги и параметры

        if len(parameters) < 2:
            return "ERROR: Необходимо указать шаблон и путь для поиска"

        # Извлекаем шаблон поиска и путь
        pattern = parameters[0]
        path = parameters[1]

        # Получаем абсолютный путь для поиска
        absolute_path = get_absolute_path(path, current_catalog)
        path_object = Path(absolute_path)

        if not path_object.exists():
            return f"ERROR: Путь не существует: {absolute_path}"

        # Создаем регулярное выражение с учетом игнорирования регистра
        if '-i' in flags: regular_flags = re.IGNORECASE
        else: regular_flags = 0
        try:
            compiled_expression = re.compile(pattern, regular_flags)
        except re.error as e:
            return f"ERROR: Неверный шаблон регулярного выражения: {str(e)}"

        if path_object.is_file():  # Если указан файл, то ищем только в нем
            files_to_search = [path_object]
        elif path_object.is_dir():
            if '-r' in flags:
                files_to_search = [f for f in path_object.rglob('*') if f.is_file()]  # Рекурсивный поиск во всех файлах каталога
            else:
                files_to_search = [f for f in path_object.iterdir() if f.is_file()]  # Поиск только в файлах текущего каталога
        else:
            return f"ERROR: Неизвестный тип объекта: {absolute_path}"

        # Выполняем поиск в файлах
        results = []
        for file_path in files_to_search:
            try:
                with open(file_path, 'r', encoding='utf-8') as file:
                    line_number = 1
                    for line in file:
                        if compiled_expression.search(line):
                            clean_line = line.strip()
                            results.append(f"{file_path}:{line_number}: {clean_line}")
                        line_number += 1
            except UnicodeDecodeError:  # Пропускаем бинарные файлы
                continue

        if results:
            return "\n".join(results)
        else:
            return "Совпадений не найдено"

    except Exception as e:
        return f"ERROR: {str(e)}"