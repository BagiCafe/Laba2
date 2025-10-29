import shutil
from pathlib import Path


def mv_command(args: str, current_catalog: str, get_absolute_path, parse_args) -> str:
    try:
        flags, parameters = parse_args(args)  # Разбираем аргументы на флаги и параметры

        if len(parameters) < 2:
            return "ERROR: Необходимо указать источник и назначение"

        # Получаем абсолютные пути для источника и назначения
        source = get_absolute_path(parameters[0], current_catalog)
        purpose = get_absolute_path(parameters[1], current_catalog)

        # Создаем объекты Path для удобной работы с путями
        source_path = Path(source)
        purpose_path = Path(purpose)

        if not source_path.exists():
            return f"ERROR: Источник не существует: {source}"

        if purpose_path.exists() and purpose_path.is_dir():  # Если назначение это существующий каталог, то мы перемещаем источник в этот каталог, сохраняя исходное имя
            purpose_path = purpose_path / source_path.name
        try:
            shutil.move(source, purpose_path)  # Перемещаем файл или каталог
            return f"Перемещено: {source} -> {purpose}"
        except Exception as e:
            return f"ERROR: Ошибка перемещения: {str(e)}"

    except Exception as e:
        return f"ERROR: {str(e)}"