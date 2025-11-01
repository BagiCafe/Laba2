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

from commands.cp import cp_command


class TestCpCommand:  # Тесты для основной функции cp_command

    def test_cp_command_file_success(self, mocker: MockerFixture):
        # Arrange
        mock_parse_args = mocker.Mock(return_value=([], ["file1.txt", "file2.txt"]))

        with patch('commands.cp.source_purpose_paths') as mock_paths:
            mock_paths.return_value = ("/current/file1.txt", "/current/file2.txt")
            with patch('commands.cp.validate_source_path') as mock_validate:
                mock_validate.return_value = (True, "/current/file1.txt")
                with patch('commands.cp.Path') as mock_path_class:
                    mock_path = Mock()
                    mock_path.is_dir.return_value = False
                    mock_path_class.return_value = mock_path
                    with patch('commands.cp.handle_file_copy') as mock_handle_file:
                        mock_handle_file.return_value = (True, "Файл скопирован: /current/file1.txt -> /current/file2.txt")

                        # Act
                        result = cp_command("file1.txt file2.txt", "/current", lambda p, c: f"{c}/{p}", mock_parse_args)

                        # Assert
                        assert "Файл скопирован" in result
                        mock_parse_args.assert_called_once_with("file1.txt file2.txt")

    def test_cp_command_directory_with_recursive_flag(self, mocker: MockerFixture):
        # Arrange
        mock_parse_args = mocker.Mock(return_value=(["-r"], ["dir1", "dir2"]))

        with patch('commands.cp.source_purpose_paths') as mock_paths:
            mock_paths.return_value = ("/current/dir1", "/current/dir2")
            with patch('commands.cp.validate_source_path') as mock_validate:
                mock_validate.return_value = (True, "/current/dir1")
                with patch('commands.cp.Path') as mock_path_class:
                    mock_path = Mock()
                    mock_path.is_dir.return_value = True
                    mock_path_class.return_value = mock_path
                    with patch('commands.cp.copy_directory_recursive') as mock_copy_dir:
                        mock_copy_dir.return_value = (True, "Каталог скопирован: /current/dir1 -> /current/dir2")

                        # Act
                        result = cp_command("-r dir1 dir2", "/current", lambda p, c: f"{c}/{p}", mock_parse_args)

                        # Assert
                        assert "Каталог скопирован" in result
                        mock_parse_args.assert_called_once_with("-r dir1 dir2")

    def test_cp_command_directory_without_recursive_flag(self, mocker: MockerFixture):
        # Arrange
        mock_parse_args = mocker.Mock(return_value=([], ["dir1", "dir2"]))

        with patch('commands.cp.source_purpose_paths') as mock_paths:
            mock_paths.return_value = ("/current/dir1", "/current/dir2")
            with patch('commands.cp.validate_source_path') as mock_validate:
                mock_validate.return_value = (True, "/current/dir1")
                with patch('commands.cp.Path') as mock_path_class:
                    mock_path = Mock()
                    mock_path.is_dir.return_value = True
                    mock_path_class.return_value = mock_path

                    # Act
                    result = cp_command("dir1 dir2", "/current", lambda p, c: f"{c}/{p}", mock_parse_args)

                    # Assert
                    assert "Используйте -r для копирования каталогов" in result
                    mock_parse_args.assert_called_once_with("dir1 dir2")

    def test_cp_command_nonexistent_source(self, mocker: MockerFixture):
        # Arrange
        mock_parse_args = mocker.Mock(return_value=([], ["nonexistent.txt", "destination.txt"]))

        with patch('commands.cp.source_purpose_paths') as mock_paths:
            mock_paths.return_value = ("/current/nonexistent.txt", "/current/destination.txt")
            with patch('commands.cp.validate_source_path') as mock_validate:
                mock_validate.return_value = (False, "ERROR: Источник не существует: /current/nonexistent.txt")

                # Act
                result = cp_command("nonexistent.txt destination.txt", "/current", lambda p, c: f"{c}/{p}", mock_parse_args)

                # Assert
                assert "ERROR: Источник не существует" in result
                mock_parse_args.assert_called_once_with("nonexistent.txt destination.txt")

    def test_cp_command_insufficient_parameters(self, mocker: MockerFixture):
        # Arrange
        mock_parse_args = mocker.Mock(return_value=([], ["file1.txt"]))

        with patch('commands.cp.source_purpose_paths') as mock_paths:
            mock_paths.return_value = ("/current/file1.txt", "")

            # Act
            result = cp_command("file1.txt", "/current", lambda p, c: f"{c}/{p}", mock_parse_args)

            # Assert
            assert "ERROR: Необходимо указать источник и назначение" in result
            mock_parse_args.assert_called_once_with("file1.txt")

    def test_cp_command_permission_error(self, mocker: MockerFixture):
        # Arrange
        mock_parse_args = mocker.Mock(return_value=([], ["file1.txt", "file2.txt"]))

        with patch('commands.cp.source_purpose_paths') as mock_paths:
            mock_paths.return_value = ("/current/file1.txt", "/current/file2.txt")
            with patch('commands.cp.validate_source_path') as mock_validate:
                mock_validate.return_value = (True, "/current/file1.txt")
                with patch('commands.cp.Path') as mock_path_class:
                    mock_path = Mock()
                    mock_path.is_dir.return_value = False
                    mock_path_class.return_value = mock_path
                    with patch('commands.cp.handle_file_copy') as mock_handle_file:
                        mock_handle_file.side_effect = PermissionError("Permission denied")

                        # Act
                        result = cp_command("file1.txt file2.txt", "/current", lambda p, c: f"{c}/{p}", mock_parse_args)

                        # Assert
                        assert "ERROR: Ошибка прав доступа" in result
                        mock_parse_args.assert_called_once_with("file1.txt file2.txt")

    def test_cp_command_general_exception(self, mocker: MockerFixture):
        # Arrange
        mock_parse_args = mocker.Mock(return_value=([], ["file1.txt", "file2.txt"]))

        with patch('commands.cp.source_purpose_paths') as mock_paths:
            mock_paths.return_value = ("/current/file1.txt", "/current/file2.txt")
            with patch('commands.cp.validate_source_path') as mock_validate:
                mock_validate.return_value = (True, "/current/file1.txt")
                with patch('commands.cp.Path') as mock_path_class:
                    mock_path = Mock()
                    mock_path.is_dir.return_value = False
                    mock_path_class.return_value = mock_path
                    with patch('commands.cp.handle_file_copy') as mock_handle_file:
                        mock_handle_file.side_effect = Exception("Unexpected error")

                        # Act
                        result = cp_command("file1.txt file2.txt", "/current", lambda p, c: f"{c}/{p}", mock_parse_args)

                        # Assert
                        assert "ERROR: Unexpected error" in result
                        mock_parse_args.assert_called_once_with("file1.txt file2.txt")

if __name__ == '__main__':
    unittest.main()