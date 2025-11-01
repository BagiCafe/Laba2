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

from commands.cd import cd_command, target_path, validate_directory


class TestTargetPath:  # Тесты для функции target_path

    def test_target_path_no_parameters(self, mocker: MockerFixture):
        # Arrange
        mock_home = mocker.Mock()
        mock_home.return_value = "/home/user"
        mocker.patch('commands.cd.Path.home', mock_home)

        # Act
        result = target_path([], "/current", lambda p, c: p)

        # Assert
        assert result == "/home/user"
        mock_home.assert_called_once()

    def test_target_path_with_absolute_path(self):
        # Act
        result = target_path(["/absolute/path"], "/current", lambda p, c: p)

        # Assert
        assert result == "/absolute/path"

    def test_target_path_with_relative_path(self):
        # Arrange
        def mock_get_absolute_path(path, current):
            return f"{current}/{path}"

        # Act
        result = target_path(["relative"], "/current", mock_get_absolute_path)

        # Assert
        assert result == "/current/relative"

    def test_target_path_with_special_characters(self, mocker: MockerFixture):
        # Arrange
        mock_home = mocker.Mock()
        mock_home.return_value = "/home/user"
        mocker.patch('commands.cd.Path.home', mock_home)

        def mock_get_absolute_path(path, current):
            return path

        # Act
        result = target_path(["~"], "/current", mock_get_absolute_path)

        # Assert
        assert result == "/home/user"


class TestValidateDirectory:  # Тесты для функции validate_directory

    def test_validate_directory_success(self):
        # Arrange
        with patch('commands.cd.Path') as mock_path_class:
            mock_path = Mock()
            mock_path.exists.return_value = True
            mock_path.is_dir.return_value = True
            mock_path_class.return_value = mock_path

            # Act
            valid, result = validate_directory("/valid/path")

            # Assert
            assert valid is True
            assert result == "/valid/path"
            mock_path.exists.assert_called_once()
            mock_path.is_dir.assert_called_once()

    def test_validate_directory_nonexistent(self):
        # Arrange
        with patch('commands.cd.Path') as mock_path_class:
            mock_path = Mock()
            mock_path.exists.return_value = False
            mock_path_class.return_value = mock_path

            # Act
            valid, result = validate_directory("/nonexistent/path")

            # Assert
            assert valid is False
            assert "ERROR: Каталог не существует" in result

    def test_validate_directory_not_a_directory(self):
        # Arrange
        with patch('commands.cd.Path') as mock_path_class:
            mock_path = Mock()
            mock_path.exists.return_value = True
            mock_path.is_dir.return_value = False
            mock_path_class.return_value = mock_path

            # Act
            valid, result = validate_directory("/file.txt")

            # Assert
            assert valid is False
            assert "ERROR: Не является каталогом" in result


class TestCdCommand:  # Тесты для основной функции cd_command

    def test_cd_command_success(self, mocker: MockerFixture):
        # Arrange
        mock_parse_args = mocker.Mock(return_value=([], ["/new/directory"]))

        with patch('commands.cd.target_path', return_value="/new/directory"):
            with patch('commands.cd.validate_directory', return_value=(True, "/new/directory")):
                # Act
                result = cd_command("/new/directory", "/current", lambda p, c: p, mock_parse_args)

                # Assert
                assert result == "/new/directory"
                mock_parse_args.assert_called_once_with("/new/directory")

    def test_cd_command_nonexistent_directory(self, mocker: MockerFixture):
        # Arrange
        mock_parse_args = mocker.Mock(return_value=([], ["/nonexistent"]))

        with patch('commands.cd.target_path', return_value="/nonexistent"):
            with patch('commands.cd.validate_directory',
                       return_value=(False, "ERROR: Каталог не существует: /nonexistent")):
                # Act
                result = cd_command("/nonexistent", "/current", lambda p, c: p, mock_parse_args)

                # Assert
                assert "ERROR: Каталог не существует" in result
                mock_parse_args.assert_called_once_with("/nonexistent")

    def test_cd_command_permission_error(self, mocker: MockerFixture):
        # Arrange
        mock_parse_args = mocker.Mock(return_value=([], ["/restricted"]))

        with patch('commands.cd.target_path', return_value="/restricted"):
            with patch('commands.cd.validate_directory',
                       side_effect=PermissionError("Permission denied")):
                # Act
                result = cd_command("/restricted", "/current", lambda p, c: p, mock_parse_args)

                # Assert
                assert "ERROR: Ошибка прав доступа" in result
                mock_parse_args.assert_called_once_with("/restricted")

    def test_cd_command_home_directory(self, mocker: MockerFixture):
        # Arrange
        mock_parse_args = mocker.Mock(return_value=([], []))
        mock_home = mocker.Mock()
        mock_home.return_value = "/home/user"
        mocker.patch('commands.cd.Path.home', mock_home)

        with patch('commands.cd.validate_directory', return_value=(True, "/home/user")):
            # Act
            result = cd_command("", "/current", lambda p, c: p, mock_parse_args)

            # Assert
            assert result == "/home/user"
            mock_parse_args.assert_called_once_with("")

    def test_cd_command_parent_directory(self, mocker: MockerFixture):
        # Arrange
        mock_parse_args = mocker.Mock(return_value=([], [".."]))

        with patch('commands.cd.target_path', return_value="/parent"):
            with patch('commands.cd.validate_directory', return_value=(True, "/parent")):
                # Act
                result = cd_command("..", "/current/subdir", lambda p, c: p, mock_parse_args)

                # Assert
                assert result == "/parent"
                mock_parse_args.assert_called_once_with("..")

    def test_cd_command_general_exception(self, mocker: MockerFixture):
        # Arrange
        mock_parse_args = mocker.Mock(return_value=([], ["/invalid"]))

        with patch('commands.cd.target_path', return_value="/invalid"):
            with patch('commands.cd.validate_directory',
                       side_effect=Exception("Unexpected error")):
                # Act
                result = cd_command("/invalid", "/current", lambda p, c: p, mock_parse_args)

                # Assert
                assert "ERROR: Unexpected error" in result
                mock_parse_args.assert_called_once_with("/invalid")

if __name__ == '__main__':
    unittest.main()