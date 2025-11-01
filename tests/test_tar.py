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


from commands.tar import tar_command, validate_archive_extension


class TestValidateArchiveExtension:  # Тесты для функции validate_archive_extension

    def test_validate_archive_extension_success(self):
        # Arrange
        with patch('commands.tar.Path') as mock_path_class:
            mock_path = Mock()
            mock_path.suffixes = ['.tar', '.gz']
            mock_path_class.return_value = mock_path

            # Act
            valid, result = validate_archive_extension("/path/archive.tar.gz")

            # Assert
            assert valid is True
            assert result == "/path/archive.tar.gz"


class TestTarCommand:  # Тесты для основной функции tar_command

    def test_tar_command_success(self, mocker: MockerFixture):
        # Arrange
        mock_parse_args = mocker.Mock(return_value=([], ["mydir", "archive.tar.gz"]))

        with patch('commands.tar.catalog_archive_paths') as mock_paths:
            mock_paths.return_value = ("/current/mydir", "/current/archive.tar.gz")
            with patch('commands.tar.validate_catalog_path') as mock_validate_catalog:
                mock_validate_catalog.return_value = (True, "/current/mydir")
                with patch('commands.tar.validate_archive_extension') as mock_validate_archive:
                    mock_validate_archive.return_value = (True, "/current/archive.tar.gz")
                    with patch('commands.tar.create_tar_archive') as mock_create_tar:
                        mock_create_tar.return_value = (True, "TAR.GZ архив создан: /current/mydir -> /current/archive.tar.gz")

                        # Act
                        result = tar_command("mydir archive.tar.gz", "/current",  lambda p, c: f"{c}/{p}", mock_parse_args)

                        # Assert
                        assert "TAR.GZ архив создан" in result
                        mock_parse_args.assert_called_once_with("mydir archive.tar.gz")

    def test_tar_command_insufficient_parameters(self, mocker: MockerFixture):
        # Arrange
        mock_parse_args = mocker.Mock(return_value=([], ["mydir"]))

        with patch('commands.tar.catalog_archive_paths') as mock_paths:
            mock_paths.return_value = ("/current/mydir", "")

            # Act
            result = tar_command("mydir", "/current", lambda p, c: f"{c}/{p}", mock_parse_args)

            # Assert
            assert "ERROR: Необходимо указать каталог и имя архива" in result
            mock_parse_args.assert_called_once_with("mydir")

    def test_tar_command_nonexistent_directory(self, mocker: MockerFixture):
        # Arrange
        mock_parse_args = mocker.Mock(return_value=([], ["nonexistent", "archive.tar.gz"]))

        with patch('commands.tar.catalog_archive_paths') as mock_paths:
            mock_paths.return_value = ("/current/nonexistent", "/current/archive.tar.gz")
            with patch('commands.tar.validate_catalog_path') as mock_validate_catalog:
                mock_validate_catalog.return_value = (False, "ERROR: Каталог не существует: /current/nonexistent")

                # Act
                result = tar_command("nonexistent archive.tar.gz", "/current", lambda p, c: f"{c}/{p}", mock_parse_args)

                # Assert
                assert "ERROR: Каталог не существует" in result
                mock_parse_args.assert_called_once_with("nonexistent archive.tar.gz")

    def test_tar_command_not_a_directory(self, mocker: MockerFixture):
        # Arrange
        mock_parse_args = mocker.Mock(return_value=([], ["file.txt", "archive.tar.gz"]))

        with patch('commands.tar.catalog_archive_paths') as mock_paths:
            mock_paths.return_value = ("/current/file.txt", "/current/archive.tar.gz")
            with patch('commands.tar.validate_catalog_path') as mock_validate_catalog:
                mock_validate_catalog.return_value = (False, "ERROR: Не является каталогом: /current/file.txt")

                # Act
                result = tar_command("file.txt archive.tar.gz", "/current", lambda p, c: f"{c}/{p}", mock_parse_args)

                # Assert
                assert "ERROR: Не является каталогом" in result
                mock_parse_args.assert_called_once_with("file.txt archive.tar.gz")

    def test_tar_command_wrong_archive_extension(self, mocker: MockerFixture):
        # Arrange
        mock_parse_args = mocker.Mock(return_value=([], ["mydir", "archive.zip"]))

        with patch('commands.tar.catalog_archive_paths') as mock_paths:
            mock_paths.return_value = ("/current/mydir", "/current/archive.zip")
            with patch('commands.tar.validate_catalog_path') as mock_validate_catalog:
                mock_validate_catalog.return_value = (True, "/current/mydir")
                with patch('commands.tar.validate_archive_extension') as mock_validate_archive:
                    mock_validate_archive.return_value = (False, "ERROR: Архив должен иметь расширение .tar.gz")

                    # Act
                    result = tar_command("mydir archive.zip", "/current", lambda p, c: f"{c}/{p}", mock_parse_args)

                    # Assert
                    assert "ERROR: Архив должен иметь расширение .tar.gz" in result
                    mock_parse_args.assert_called_once_with("mydir archive.zip")

    def test_tar_command_archive_creation_error(self, mocker: MockerFixture):
        # Arrange
        mock_parse_args = mocker.Mock(return_value=([], ["mydir", "archive.tar.gz"]))

        with patch('commands.tar.catalog_archive_paths') as mock_paths:
            mock_paths.return_value = ("/current/mydir", "/current/archive.tar.gz")
            with patch('commands.tar.validate_catalog_path') as mock_validate_catalog:
                mock_validate_catalog.return_value = (True, "/current/mydir")
                with patch('commands.tar.validate_archive_extension') as mock_validate_archive:
                    mock_validate_archive.return_value = (True, "/current/archive.tar.gz")
                    with patch('commands.tar.create_tar_archive') as mock_create_tar:
                        mock_create_tar.return_value = (False, "ERROR: Ошибка создания архива: Disk full")

                        # Act
                        result = tar_command("mydir archive.tar.gz", "/current", lambda p, c: f"{c}/{p}", mock_parse_args)

                        # Assert
                        assert "ERROR: Ошибка создания архива" in result
                        mock_parse_args.assert_called_once_with("mydir archive.tar.gz")

    def test_tar_command_permission_error(self, mocker: MockerFixture):
        # Arrange
        mock_parse_args = mocker.Mock(return_value=([], ["mydir", "archive.tar.gz"]))

        with patch('commands.tar.catalog_archive_paths') as mock_paths:
            mock_paths.return_value = ("/current/mydir", "/current/archive.tar.gz")
            with patch('commands.tar.validate_catalog_path') as mock_validate_catalog:
                mock_validate_catalog.side_effect = PermissionError("Permission denied")

                # Act
                result = tar_command("mydir archive.tar.gz", "/current", lambda p, c: f"{c}/{p}", mock_parse_args)

                # Assert
                assert "ERROR: Ошибка прав доступа" in result
                mock_parse_args.assert_called_once_with("mydir archive.tar.gz")

if __name__ == '__main__':
    unittest.main()
