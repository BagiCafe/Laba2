from unittest.mock import Mock, patch
from pytest_mock import MockerFixture
import sys
import os
import unittest

# Добавляем пути для импорта
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
src_dir = os.path.join(parent_dir, 'src')
sys.path.insert(0, src_dir)

from commands.zip import zip_command, validate_archive_extension


class TestValidateArchiveExtension:  # Тесты для функции validate_archive_extension

    def test_validate_archive_extension_success(self):
        # Arrange
        with patch('commands.zip.Path') as mock_path_class:
            mock_path = Mock()
            mock_path.suffix = '.zip'
            mock_path_class.return_value = mock_path

            # Act
            valid, result = validate_archive_extension("/path/archive.zip")

            # Assert
            assert valid is True
            assert result == "/path/archive.zip"


class TestZipCommand:  # Тесты для основной функции zip_command

    def test_zip_command_success(self, mocker: MockerFixture):
        # Arrange
        mock_parse_args = mocker.Mock(return_value=([], ["mydir", "archive.zip"]))

        with patch('commands.zip.catalog_archive_paths') as mock_paths:
            mock_paths.return_value = ("/current/mydir", "/current/archive.zip")
            with patch('commands.zip.validate_catalog_path') as mock_validate_catalog:
                mock_validate_catalog.return_value = (True, "/current/mydir")
                with patch('commands.zip.validate_archive_extension') as mock_validate_archive:
                    mock_validate_archive.return_value = (True, "/current/archive.zip")
                    with patch('commands.zip.create_zip_archive') as mock_create_zip:
                        mock_create_zip.return_value = (True, "ZIP-архив создан: /current/mydir -> /current/archive.zip")

                        # Act
                        result = zip_command("mydir archive.zip", "/current", lambda p, c: f"{c}/{p}", mock_parse_args)

                        # Assert
                        assert "ZIP-архив создан" in result
                        mock_parse_args.assert_called_once_with("mydir archive.zip")

    def test_zip_command_insufficient_parameters(self, mocker: MockerFixture):
        # Arrange
        mock_parse_args = mocker.Mock(return_value=([], ["mydir"]))

        with patch('commands.zip.catalog_archive_paths') as mock_paths:
            mock_paths.return_value = ("/current/mydir", "")

            # Act
            result = zip_command("mydir", "/current", lambda p, c: f"{c}/{p}", mock_parse_args)

            # Assert
            assert "ERROR: Необходимо указать каталог и имя архива" in result
            mock_parse_args.assert_called_once_with("mydir")

    def test_zip_command_nonexistent_directory(self, mocker: MockerFixture):
        # Arrange
        mock_parse_args = mocker.Mock(return_value=([], ["nonexistent", "archive.zip"]))

        with patch('commands.zip.catalog_archive_paths') as mock_paths:
            mock_paths.return_value = ("/current/nonexistent", "/current/archive.zip")
            with patch('commands.zip.validate_catalog_path') as mock_validate_catalog:
                mock_validate_catalog.return_value = (False, "ERROR: Каталог не существует: /current/nonexistent")

                # Act
                result = zip_command("nonexistent archive.zip", "/current", lambda p, c: f"{c}/{p}", mock_parse_args)

                # Assert
                assert "ERROR: Каталог не существует" in result
                mock_parse_args.assert_called_once_with("nonexistent archive.zip")

    def test_zip_command_wrong_archive_extension(self, mocker: MockerFixture):
        # Arrange
        mock_parse_args = mocker.Mock(return_value=([], ["mydir", "archive.rar"]))

        with patch('commands.zip.catalog_archive_paths') as mock_paths:
            mock_paths.return_value = ("/current/mydir", "/current/archive.rar")
            with patch('commands.zip.validate_catalog_path') as mock_validate_catalog:
                mock_validate_catalog.return_value = (True, "/current/mydir")
                with patch('commands.zip.validate_archive_extension') as mock_validate_archive:
                    mock_validate_archive.return_value = (False, "ERROR: Имя архива должно иметь расширение .zip")

                    # Act
                    result = zip_command("mydir archive.rar", "/current", lambda p, c: f"{c}/{p}", mock_parse_args)

                    # Assert
                    assert "ERROR: Имя архива должно иметь расширение .zip" in result
                    mock_parse_args.assert_called_once_with("mydir archive.rar")

    def test_zip_command_archive_creation_error(self, mocker: MockerFixture):
        # Arrange
        mock_parse_args = mocker.Mock(return_value=([], ["mydir", "archive.zip"]))

        with patch('commands.zip.catalog_archive_paths') as mock_paths:
            mock_paths.return_value = ("/current/mydir", "/current/archive.zip")
            with patch('commands.zip.validate_catalog_path') as mock_validate_catalog:
                mock_validate_catalog.return_value = (True, "/current/mydir")
                with patch('commands.zip.validate_archive_extension') as mock_validate_archive:
                    mock_validate_archive.return_value = (True, "/current/archive.zip")
                    with patch('commands.zip.create_zip_archive') as mock_create_zip:
                        mock_create_zip.return_value = (False, "ERROR: Ошибка создания архива: Disk full")

                        # Act
                        result = zip_command("mydir archive.zip", "/current", lambda p, c: f"{c}/{p}", mock_parse_args)

                        # Assert
                        assert "ERROR: Ошибка создания архива" in result
                        mock_parse_args.assert_called_once_with("mydir archive.zip")

    def test_zip_command_permission_error(self, mocker: MockerFixture):
        # Arrange
        mock_parse_args = mocker.Mock(return_value=([], ["mydir", "archive.zip"]))

        with patch('commands.zip.catalog_archive_paths') as mock_paths:
            mock_paths.return_value = ("/current/mydir", "/current/archive.zip")
            with patch('commands.zip.validate_catalog_path') as mock_validate_catalog:
                mock_validate_catalog.side_effect = PermissionError("Permission denied")

                # Act
                result = zip_command("mydir archive.zip", "/current", lambda p, c: f"{c}/{p}", mock_parse_args)

                # Assert
                assert "ERROR: Ошибка прав доступа" in result
                mock_parse_args.assert_called_once_with("mydir archive.zip")

    def test_zip_command_general_exception(self, mocker: MockerFixture):
        # Arrange
        mock_parse_args = mocker.Mock(return_value=([], ["mydir", "archive.zip"]))

        with patch('commands.zip.catalog_archive_paths') as mock_paths:
            mock_paths.return_value = ("/current/mydir", "/current/archive.zip")
            with patch('commands.zip.validate_catalog_path') as mock_validate_catalog:
                mock_validate_catalog.side_effect = Exception("Unexpected error")

                # Act
                result = zip_command("mydir archive.zip", "/current", lambda p, c: f"{c}/{p}", mock_parse_args)

                # Assert
                assert "ERROR: Unexpected error" in result
                mock_parse_args.assert_called_once_with("mydir archive.zip")

if __name__ == '__main__':
    unittest.main()