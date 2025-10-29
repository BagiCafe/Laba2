import shutil
from pathlib import Path


def cp_command(args: str, current_catalog: str, get_absolute_path, parse_args) -> str:
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

        if '-r' in flags:
            if source_path.is_dir():
                try:
                    shutil.copytree(source, purpose_path)  # Рекурсивно копируем весь каталог с содержимым
                    return f"Каталог скопирован: {source} -> {purpose}"
                except Exception as e:
                    return f"ERROR: Ошибка копирования каталога: {str(e)}"
            else:
                return "ERROR: Флаг -r применяется только к каталогам"
        else:
            if source_path.is_dir():
                return "ERROR: Используйте -r для копирования каталогов"

            try:
                shutil.copy2(source, purpose_path)
                return f"Файл скопирован: {source} -> {purpose}"
            except Exception as e:
                return f"ERROR: Ошибка копирования файла: {str(e)}"

    except Exception as e:
        return f"ERROR: {str(e)}"