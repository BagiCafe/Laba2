import shutil
from pathlib import Path


def rm_command(args: str, current_catalog: str, get_absolute_path, parse_args) -> str:
    try:
        flags, parameters = parse_args(args)  # Разбираем аргументы на флаги и параметры

        if not parameters:
            return "ERROR: Не указан файл/каталог для удаления"

        target = get_absolute_path(parameters[0], current_catalog)  # Получаем абсолютный путь к целевому объекту
        target_path = Path(target)  # Создаем объект Path для удобной работы с путем

        if not target_path.exists():
            return f"ERROR: Файл/каталог не существует: {target}"

        root_path = Path(target_path.root)
        if target_path.resolve() == root_path:
            return "ERROR: Запрещено удалять корневой каталог"

        parent_path = Path(current_catalog).parent.resolve()
        if target_path.resolve() == parent_path:
            return "ERROR: Запрещено удалять родительский каталог"

        if target_path.is_dir():
            if '-r' not in flags:
                return "ERROR: Используйте -r для удаления каталогов"

            confirmation = input(f"Удалить каталог '{target}'? (y/n): ")
            if confirmation.lower() == 'n':
                return "Удаление отменено"

            try:
                shutil.rmtree(target_path)  # Рекурсивно удаляем каталог со всем содержимым
                return f"Каталог удален: {target}"
            except Exception as e:
                return f"ERROR: Ошибка удаления каталога: {str(e)}"
        else:
            try:
                target_path.unlink()  # Удаляем файл
                return f"Файл удален: {target}"
            except Exception as e:
                return f"ERROR: Ошибка удаления файла: {str(e)}"

    except Exception as e:
        return f"ERROR: {str(e)}"