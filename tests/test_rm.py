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

from commands.rm import rm_command




class TestRmCommand:  # Тесты для основной функции rm_command

    def test_rm_command_file_success(self, mocker: MockerFixture):
        # Arrange
        mock_parse_args = mocker.Mock(return_value=([], ["file.txt"]))

        with patch('commands.rm.target_path') as mock_target:
            mock_target.return_value = "/current/file.txt"
            with patch('commands.rm.validate_target_path') as mock_validate:
                mock_validate.return_value = (True, "/current/file.txt")
                with patch('commands.rm.Path') as mock_path_class:
                    mock_path = Mock()
                    mock_path.is_dir.return_value = False
                    mock_path_class.return_value = mock_path
                    with patch('commands.rm.delete_file') as mock_delete_file:
                        mock_delete_file.return_value = (True, "Файл удален: /current/file.txt")

                        # Act
                        result = rm_command("file.txt", "/current", lambda p, c: f"{c}/{p}", mock_parse_args)

                        # Assert
                        assert "Файл удален" in result
                        mock_parse_args.assert_called_once_with("file.txt")

    def test_rm_command_directory_with_recursive_flag(self, mocker: MockerFixture):
        # Arrange
        mock_parse_args = mocker.Mock(return_value=(["-r"], ["directory"]))

        with patch('commands.rm.target_path') as mock_target:
            mock_target.return_value = "/current/directory"
            with patch('commands.rm.validate_target_path') as mock_validate:
                mock_validate.return_value = (True, "/current/directory")
                with patch('commands.rm.Path') as mock_path_class:
                    mock_path = Mock()
                    mock_path.is_dir.return_value = True
                    mock_path_class.return_value = mock_path
                    with patch('commands.rm.delete_catalog') as mock_delete_dir:
                        mock_delete_dir.return_value = (True, "Каталог удален: /current/directory")

                        # Act
                        result = rm_command("-r directory", "/current", lambda p, c: f"{c}/{p}", mock_parse_args)

                        # Assert
                        assert "Каталог удален" in result
                        mock_parse_args.assert_called_once_with("-r directory")

    def test_rm_command_directory_without_recursive_flag(self, mocker: MockerFixture):
        # Arrange
        mock_parse_args = mocker.Mock(return_value=([], ["directory"]))

        with patch('commands.rm.target_path') as mock_target:
            mock_target.return_value = "/current/directory"
            with patch('commands.rm.validate_target_path') as mock_validate:
                mock_validate.return_value = (True, "/current/directory")
                with patch('commands.rm.Path') as mock_path_class:
                    mock_path = Mock()
                    mock_path.is_dir.return_value = True
                    mock_path_class.return_value = mock_path

                    # Act
                    result = rm_command("directory", "/current", lambda p, c: f"{c}/{p}", mock_parse_args)

                    # Assert
                    assert "Используйте -r для удаления каталогов" in result
                    mock_parse_args.assert_called_once_with("directory")

    def test_rm_command_nonexistent_target(self, mocker: MockerFixture):
        # Arrange
        mock_parse_args = mocker.Mock(return_value=([], ["nonexistent.txt"]))

        with patch('commands.rm.target_path') as mock_target:
            mock_target.return_value = "/current/nonexistent.txt"
            with patch('commands.rm.validate_target_path') as mock_validate:
                mock_validate.return_value = (False, "ERROR: Файл/каталог не существует: /current/nonexistent.txt")

                # Act
                result = rm_command("nonexistent.txt", "/current", lambda p, c: f"{c}/{p}", mock_parse_args)

                # Assert
                assert "ERROR: Файл/каталог не существует" in result
                mock_parse_args.assert_called_once_with("nonexistent.txt")

    def test_rm_command_root_directory_protection(self, mocker: MockerFixture):
        # Arrange
        mock_parse_args = mocker.Mock(return_value=(["-r"], ["C:\\"]))

        with patch('commands.rm.target_path') as mock_target:
            mock_target.return_value = "C:\\"
            with patch('commands.rm.validate_target_path') as mock_validate:
                mock_validate.return_value = (False, "ERROR: Запрещено удалять корневой каталог")

                # Act
                result = rm_command("-r C:\\", "/current", lambda p, c: f"{c}/{p}", mock_parse_args)

                # Assert
                assert "ERROR: Запрещено удалять корневой каталог" in result
                mock_parse_args.assert_called_once_with("-r C:\\")

    def test_rm_command_no_target_specified(self, mocker: MockerFixture):
        # Arrange
        mock_parse_args = mocker.Mock(return_value=([], []))

        with patch('commands.rm.target_path') as mock_target:
            mock_target.return_value = ""

            # Act
            result = rm_command("", "/current", lambda p, c: f"{c}/{p}", mock_parse_args)

            # Assert
            assert "ERROR: Не указан файл/каталог для удаления" in result
            mock_parse_args.assert_called_once_with("")

    def test_rm_command_permission_error(self, mocker: MockerFixture):
        # Arrange
        mock_parse_args = mocker.Mock(return_value=([], ["file.txt"]))

        with patch('commands.rm.target_path') as mock_target:
            mock_target.return_value = "/current/file.txt"
            with patch('commands.rm.validate_target_path') as mock_validate:
                mock_validate.side_effect = PermissionError("Permission denied")

                # Act
                result = rm_command("file.txt", "/current", lambda p, c: f"{c}/{p}", mock_parse_args)

                # Assert
                assert "ERROR: Ошибка прав доступа" in result
                mock_parse_args.assert_called_once_with("file.txt")


    def test_rm_command_user_cancels_directory_deletion(self, mocker: MockerFixture):
        # Arrange
        mock_parse_args = mocker.Mock(return_value=(["-r"], ["directory"]))

        with patch('commands.rm.target_path') as mock_target:
            mock_target.return_value = "/current/directory"
            with patch('commands.rm.validate_target_path') as mock_validate:
                mock_validate.return_value = (True, "/current/directory")
                with patch('commands.rm.Path') as mock_path_class:
                    mock_path = Mock()
                    mock_path.is_dir.return_value = True
                    mock_path_class.return_value = mock_path
                    with patch('commands.rm.delete_catalog') as mock_delete_dir:
                        mock_delete_dir.return_value = (False, "Удаление отменено")

                        # Act
                        result = rm_command("-r directory", "/current", lambda p, c: f"{c}/{p}", mock_parse_args)

                        # Assert
                        assert "Удаление отменено" in result
                        mock_parse_args.assert_called_once_with("-r directory")

if __name__ == '__main__':
    unittest.main()