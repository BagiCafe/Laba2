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

from commands.untar import untar_command, validate_target_directory


class TestValidateTargetDirectory:  # Тесты для функции validate_target_directory

    def test_validate_target_directory_create_success(self):
        # Arrange
        with patch('commands.untar.Path') as mock_path_class:
            mock_path = Mock()
            mock_path.exists.return_value = False
            mock_path.is_dir.return_value = True
            mock_path_class.return_value = mock_path

            with patch('commands.untar.create_target_directory') as mock_create:
                mock_create.return_value = (True, "/new/dir")

                # Act
                valid, result = validate_target_directory("/new/dir")

                # Assert
                assert valid is True
                assert result == "/new/dir"


class TestUntarCommand:  # Тесты для основной функции untar_command
    def test_untar_command_no_archive_specified(self, mocker: MockerFixture):
        # Arrange
        mock_parse_args = mocker.Mock(return_value=([], []))

        with patch('commands.untar.archive_target_paths') as mock_paths:
            mock_paths.return_value = ("", "/current")

            # Act
            result = untar_command("", "/current", lambda p, c: f"{c}/{p}", mock_parse_args)

            # Assert
            assert "ERROR: Не указан архив для распаковки" in result
            mock_parse_args.assert_called_once_with("")

    def test_untar_command_nonexistent_archive(self, mocker: MockerFixture):
        # Arrange
        mock_parse_args = mocker.Mock(return_value=([], ["nonexistent.tar.gz"]))

        with patch('commands.untar.archive_target_paths') as mock_paths:
            mock_paths.return_value = ("/current/nonexistent.tar.gz", "/current")
            with patch('commands.untar.validate_archive_path') as mock_validate_archive:
                mock_validate_archive.return_value = (False, "ERROR: Архив не существует: /current/nonexistent.tar.gz")

                # Act
                result = untar_command("nonexistent.tar.gz", "/current", lambda p, c: f"{c}/{p}", mock_parse_args)

                # Assert
                assert "ERROR: Архив не существует" in result
                mock_parse_args.assert_called_once_with("nonexistent.tar.gz")

    def test_untar_command_wrong_archive_format(self, mocker: MockerFixture):
        # Arrange
        mock_parse_args = mocker.Mock(return_value=([], ["archive.zip"]))

        with patch('commands.untar.archive_target_paths') as mock_paths:
            mock_paths.return_value = ("/current/archive.zip", "/current")
            with patch('commands.untar.validate_archive_path') as mock_validate_archive:
                mock_validate_archive.return_value = (True, "/current/archive.zip")
                with patch('commands.untar.validate_archive_format') as mock_validate_format:
                    mock_validate_format.return_value = (False, "ERROR: Файл не является TAR архивом")

                    # Act
                    result = untar_command("archive.zip", "/current", lambda p, c: f"{c}/{p}", mock_parse_args)

                    # Assert
                    assert "ERROR: Файл не является TAR архивом" in result
                    mock_parse_args.assert_called_once_with("archive.zip")

    def test_untar_command_extraction_error(self, mocker: MockerFixture):
        # Arrange
        mock_parse_args = mocker.Mock(return_value=([], ["archive.tar.gz"]))

        with patch('commands.untar.archive_target_paths') as mock_paths:
            mock_paths.return_value = ("/current/archive.tar.gz", "/current")
            with patch('commands.untar.validate_archive_path') as mock_validate_archive:
                mock_validate_archive.return_value = (True, "/current/archive.tar.gz")
                with patch('commands.untar.validate_archive_format') as mock_validate_format:
                    mock_validate_format.return_value = (True, "/current/archive.tar.gz")
                    with patch('commands.untar.validate_target_directory') as mock_validate_target:
                        mock_validate_target.return_value = (True, "/current")
                        with patch('commands.untar.extract_tar_archive') as mock_extract:
                            mock_extract.return_value = (False, "ERROR: Ошибка распаковки архива: Corrupted file")

                            # Act
                            result = untar_command("archive.tar.gz", "/current", lambda p, c: f"{c}/{p}", mock_parse_args)

                            # Assert
                            assert "ERROR: Ошибка распаковки архива" in result
                            mock_parse_args.assert_called_once_with("archive.tar.gz")

    def test_untar_command_permission_error(self, mocker: MockerFixture):
        # Arrange
        mock_parse_args = mocker.Mock(return_value=([], ["archive.tar.gz"]))

        with patch('commands.untar.archive_target_paths') as mock_paths:
            mock_paths.return_value = ("/current/archive.tar.gz", "/current")
            with patch('commands.untar.validate_archive_path') as mock_validate_archive:
                mock_validate_archive.side_effect = PermissionError("Permission denied")

                # Act
                result = untar_command("archive.tar.gz", "/current", lambda p, c: f"{c}/{p}", mock_parse_args)

                # Assert
                assert "ERROR: Ошибка прав доступа" in result
                mock_parse_args.assert_called_once_with("archive.tar.gz")

if __name__ == '__main__':
    unittest.main()