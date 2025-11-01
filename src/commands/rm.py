import shutil
from pathlib import Path


def get_target_path(parameters: list, current_catalog: str, get_absolute_path) -> str:  # Получаем абсолютный путь к целевому объекту
    if not parameters:
        return ""
    return get_absolute_path(parameters[0], current_catalog)

def validate_target_path(target: str, current_catalog: str) -> tuple:  # Проверяем существование объекта и запрещенные пути
    target_path = Path(target)  # Создаем объект Path для удобной работы с путем
    if not target_path.exists():
        return False, f"ERROR: Файл/каталог не существует: {target}"
    root_path = Path(target_path.root)
    if target_path.resolve() == root_path:
        return False, "ERROR: Запрещено удалять корневой каталог"
    parent_path = Path(current_catalog).parent.resolve()
    if target_path.resolve() == parent_path:
        return False, "ERROR: Запрещено удалять родительский каталог"
    return True, target


def confirm_catalog(target: str) -> bool:  # Запрашиваем подтверждение на удаление каталога
    confirmation = input(f"Удалить каталог '{target}'? (y/n): ")
    return confirmation.lower() == 'y'


def delete_catalog(target_path: Path, recursive: bool) -> tuple:  # Удаляем каталог
    if not recursive:
        return False, "ERROR: Используйте -r для удаления каталогов"
    if not confirm_catalog(str(target_path)):
        return False, "Удаление отменено"
    try:
        shutil.rmtree(target_path)
        return True, f"Каталог удален: {target_path}"
    except Exception as e:
        return False, f"ERROR: Ошибка удаления каталога: {str(e)}"


def delete_file(target_path: Path) -> tuple:  # Удаляем файл
    try:
        target_path.unlink()
        return True, f"Файл удален: {target_path}"
    except Exception as e:
        return False, f"ERROR: Ошибка удаления файла: {str(e)}"


def rm_command(args: str, current_catalog: str, get_absolute_path, parse_args) -> str:
    try:
        flags, parameters = parse_args(args)  # Разбираем аргументы на флаги и параметры
        target = get_target_path(parameters, current_catalog, get_absolute_path)
        if not target:
            return "ERROR: Не указан файл/каталог для удаления"
        valid, validation_result = validate_target_path(target, current_catalog)
        if not valid:
            return validation_result
        target_path = Path(validation_result)
        recursive = '-r' in flags  # Проверяем флаг рекурсивного удаления
        if target_path.is_dir():
            success, result = delete_catalog(target_path, recursive)
        else:
            success, result = delete_file(target_path)
        return result
    except Exception as e:
        return f"ERROR: {str(e)}"