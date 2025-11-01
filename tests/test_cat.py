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

from commands.cat import (cat_command, validate_file)


class TestValidateFile:  # Тесты для функции validate_file

    def test_validate_file_success(self):
        # Arrange
        with patch('commands.cat.Path') as mock_path_class:
            mock_path = Mock()
            mock_path.exists.return_value = True
            mock_path.is_dir.return_value = False
            mock_path_class.return_value = mock_path

            # Act
            valid, result = validate_file("/valid/file.txt")

            # Assert
            assert valid is True
            assert result == "/valid/file.txt"
            mock_path.exists.assert_called_once()
            mock_path.is_dir.assert_called_once()

    def test_validate_file_nonexistent(self):
        # Arrange
        with patch('commands.cat.Path') as mock_path_class:
            mock_path = Mock()
            mock_path.exists.return_value = False
            mock_path_class.return_value = mock_path

            # Act
            valid, result = validate_file("/nonexistent/file.txt")

            # Assert
            assert valid is False
            assert "ERROR: Файл не существует" in result

    def test_validate_file_is_directory(self):
        # Arrange
        with patch('commands.cat.Path') as mock_path_class:
            mock_path = Mock()
            mock_path.exists.return_value = True
            mock_path.is_dir.return_value = True
            mock_path_class.return_value = mock_path

            # Act
            valid, result = validate_file("/directory")

            # Assert
            assert valid is False
            assert "ERROR: Является каталогом" in result


class TestCatCommand:  # Тесты для основной функции cat_command

    def test_cat_command_success(self, mocker: MockerFixture):
        # Arrange
        mock_parse_args = mocker.Mock(return_value=([], ["file.txt"]))
        mock_content = "File content line 1\nLine 2\nLine 3"

        with patch('commands.cat.get_file_path') as mock_get_path:
            mock_get_path.return_value = "/current/file.txt"
            with patch('commands.cat.validate_file') as mock_validate:
                mock_validate.return_value = (True, "/current/file.txt")
                with patch('commands.cat.read_file') as mock_read:
                    mock_read.return_value = (True, mock_content)

                    # Act
                    result = cat_command("file.txt", "/current", lambda p, c: f"{c}/{p}", mock_parse_args)

                    # Assert
                    assert result == mock_content
                    mock_parse_args.assert_called_once_with("file.txt")

    def test_cat_command_no_file_specified(self, mocker: MockerFixture):
        # Arrange
        mock_parse_args = mocker.Mock(return_value=([], []))

        with patch('commands.cat.get_file_path') as mock_get_path:
            mock_get_path.return_value = ""

            # Act
            result = cat_command("", "/current", lambda p, c: f"{c}/{p}", mock_parse_args)

            # Assert
            assert "ERROR: Не указан файл" in result
            mock_parse_args.assert_called_once_with("")

    def test_cat_command_nonexistent_file(self, mocker: MockerFixture):
        # Arrange
        mock_parse_args = mocker.Mock(return_value=([], ["nonexistent.txt"]))

        with patch('commands.cat.get_file_path') as mock_get_path:
            mock_get_path.return_value = "/current/nonexistent.txt"
            with patch('commands.cat.validate_file') as mock_validate:
                mock_validate.return_value = (False, "ERROR: Файл не существует: /current/nonexistent.txt")

                # Act
                result = cat_command("nonexistent.txt", "/current", lambda p, c: f"{c}/{p}", mock_parse_args)

                # Assert
                assert "ERROR: Файл не существует" in result
                mock_parse_args.assert_called_once_with("nonexistent.txt")

    def test_cat_command_directory_instead_of_file(self, mocker: MockerFixture):
        # Arrange
        mock_parse_args = mocker.Mock(return_value=([], ["directory"]))

        with patch('commands.cat.get_file_path') as mock_get_path:
            mock_get_path.return_value = "/current/directory"
            with patch('commands.cat.validate_file') as mock_validate:
                mock_validate.return_value = (False, "ERROR: Является каталогом: /current/directory")

                # Act
                result = cat_command("directory", "/current", lambda p, c: f"{c}/{p}", mock_parse_args)

                # Assert
                assert "ERROR: Является каталогом" in result
                mock_parse_args.assert_called_once_with("directory")

    def test_cat_command_read_error(self, mocker: MockerFixture):
        # Arrange
        mock_parse_args = mocker.Mock(return_value=([], ["file.txt"]))

        with patch('commands.cat.get_file_path') as mock_get_path:
            mock_get_path.return_value = "/current/file.txt"
            with patch('commands.cat.validate_file') as mock_validate:
                mock_validate.return_value = (True, "/current/file.txt")
                with patch('commands.cat.read_file') as mock_read:
                    mock_read.return_value = (False, "ERROR: Не удается прочитать файл")

                    # Act
                    result = cat_command("file.txt", "/current", lambda p, c: f"{c}/{p}", mock_parse_args)

                    # Assert
                    assert "ERROR: Не удается прочитать файл" in result
                    mock_parse_args.assert_called_once_with("file.txt")

    def test_cat_command_permission_error(self, mocker: MockerFixture):
        # Arrange
        mock_parse_args = mocker.Mock(return_value=([], ["restricted.txt"]))

        with patch('commands.cat.get_file_path') as mock_get_path:
            mock_get_path.return_value = "/current/restricted.txt"
            with patch('commands.cat.validate_file') as mock_validate:
                mock_validate.side_effect = PermissionError("Permission denied")

                # Act
                result = cat_command("restricted.txt", "/current", lambda p, c: f"{c}/{p}", mock_parse_args)

                # Assert
                assert "ERROR: Ошибка прав доступа" in result
                mock_parse_args.assert_called_once_with("restricted.txt")

    def test_cat_command_general_exception(self, mocker: MockerFixture):
        # Arrange
        mock_parse_args = mocker.Mock(return_value=([], ["file.txt"]))

        with patch('commands.cat.get_file_path') as mock_get_path:
            mock_get_path.return_value = "/current/file.txt"
            with patch('commands.cat.validate_file') as mock_validate:
                mock_validate.side_effect = Exception("Unexpected error")

                # Act
                result = cat_command("file.txt", "/current", lambda p, c: f"{c}/{p}", mock_parse_args)

                # Assert
                assert "ERROR: Unexpected error" in result
                mock_parse_args.assert_called_once_with("file.txt")

    def test_cat_command_with_flags(self, mocker: MockerFixture):
        # Arrange
        mock_parse_args = mocker.Mock(return_value=(["-n"], ["file.txt"]))
        mock_content = "Line 1\nLine 2"

        with patch('commands.cat.get_file_path') as mock_get_path:
            mock_get_path.return_value = "/current/file.txt"
            with patch('commands.cat.validate_file') as mock_validate:
                mock_validate.return_value = (True, "/current/file.txt")
                with patch('commands.cat.read_file') as mock_read:
                    mock_read.return_value = (True, mock_content)

                    # Act
                    result = cat_command("-n file.txt", "/current", lambda p, c: f"{c}/{p}", mock_parse_args)

                    # Assert
                    # Флаги игнорируются в текущей реализации, но команда должна работать
                    assert result == mock_content
                    mock_parse_args.assert_called_once_with("-n file.txt")

if __name__ == '__main__':
    unittest.main()