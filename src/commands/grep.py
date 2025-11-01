import re
from pathlib import Path


def pattern_search_path(parameters: list, current_catalog: str, get_absolute_path) -> tuple:  # Получаем шаблон поиска и путь для поиска
    if len(parameters) < 2:
        return "", ""
    pattern = parameters[0]
    path = parameters[1]
    absolute_path = get_absolute_path(path, current_catalog)
    return pattern, absolute_path


def validate_search_path(search_path: str) -> tuple:  # Проверяем существование пути поиска
    path_object = Path(search_path)
    if not path_object.exists():
        return False, f"ERROR: Путь не существует: {search_path}"
    return True, search_path


def compile_pattern(pattern: str, ignore_case: bool) -> tuple:  # Компилируем регулярное выражение
    if ignore_case: flags = re.IGNORECASE
    else: flags = 0
    try:
        compiled_expression = re.compile(pattern, flags)
        return True, compiled_expression
    except re.error as e:
        return False, f"ERROR: Неверный шаблон регулярного выражения: {str(e)}"


def files_search(search_path: str, recursive: bool) -> tuple:  # Получаем список файлов для поиска
    path_object = Path(search_path)
    if path_object.is_file():  # Если указан файл, то ищем только в нем
        files_to_search = [path_object]
    elif path_object.is_dir():
        if recursive:
            files_to_search = [f for f in path_object.rglob('*') if f.is_file()]  # Рекурсивный поиск во всех файлах каталога
        else:
            files_to_search = [f for f in path_object.iterdir() if f.is_file()]  # Поиск только в файлах текущего каталога
    else:
        return False, f"ERROR: Неизвестный тип объекта: {search_path}"
    return True, files_to_search


def search_file(file_path: Path, compiled_pattern: any) -> list:  # Ищем совпадения в одном файле
    results = []
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            line_number = 1
            for line in file:
                if compiled_pattern.search(line):
                    clean_line = line.strip()
                    results.append(f"{file_path}:{line_number}: {clean_line}")
                line_number += 1
    except UnicodeDecodeError:  # Пропускаем бинарные файлы
        pass
    except Exception as e:
        results.append(f"{file_path}: ERROR: {str(e)}")
    return results


def perform_search(files_to_search: list, compiled_pattern: any) -> list:  # Выполняем поиск во всех файлах
    all_results = []
    for file_path in files_to_search:
        file_results = search_file(file_path, compiled_pattern)
        all_results.extend(file_results)
    return all_results


def format_results(results: list) -> str:  # Форматируем результаты поиска
    if results:
        return "\n".join(results)
    else:
        return "Совпадений не найдено"


def grep_command(args: str, current_catalog: str, get_absolute_path, parse_args) -> str:
    try:
        flags, parameters = parse_args(args)  # Разбираем аргументы на флаги и параметры
        pattern, search_path = pattern_search_path(parameters, current_catalog, get_absolute_path)
        if not pattern or not search_path:
            return "ERROR: Необходимо указать шаблон и путь для поиска"

        path_valid, path_result = validate_search_path(search_path)
        if not path_valid:
            return path_result

        ignore_case = '-i' in flags
        pattern_valid, pattern_result = compile_pattern(pattern, ignore_case)
        if not pattern_valid:
            return pattern_result

        recursive = '-r' in flags
        files_valid, files_result = files_search(path_result, recursive)
        if not files_valid:
            return files_result

        search_results = perform_search(files_result, pattern_result)
        return format_results(search_results)
    except Exception as e:
        return f"ERROR: {str(e)}"