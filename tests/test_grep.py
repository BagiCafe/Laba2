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

from commands.grep import grep_command, files_search


class TestFilesSearch:  # Тесты для функции files_search

    def test_files_search_single_file(self):
        # Arrange
        with patch('commands.grep.Path') as mock_path_class:
            mock_path = Mock()
            mock_path.is_file.return_value = True
            mock_path.is_dir.return_value = False
            mock_path_class.return_value = mock_path

            # Act
            success, result = files_search("/single/file.txt", False)

            # Assert
            assert success is True
            assert len(result) == 1
            assert result[0] == mock_path


class TestGrepCommand:  # Тесты для основной функции grep_command
    def test_grep_command_insufficient_parameters(self, mocker: MockerFixture):
        # Arrange
        mock_parse_args = mocker.Mock(return_value=([], ["hello"]))

        with patch('commands.grep.pattern_search_path') as mock_pattern_path:
            mock_pattern_path.return_value = ("hello", "")

            # Act
            result = grep_command("hello", "/current", lambda p, c: f"{c}/{p}", mock_parse_args)

            # Assert
            assert "ERROR: Необходимо указать шаблон и путь для поиска" in result
            mock_parse_args.assert_called_once_with("hello")

    def test_grep_command_nonexistent_path(self, mocker: MockerFixture):
        # Arrange
        mock_parse_args = mocker.Mock(return_value=([], ["hello", "nonexistent"]))

        with patch('commands.grep.pattern_search_path') as mock_pattern_path:
            mock_pattern_path.return_value = ("hello", "/current/nonexistent")
            with patch('commands.grep.validate_search_path') as mock_validate:
                mock_validate.return_value = (False, "ERROR: Путь не существует: /current/nonexistent")

                # Act
                result = grep_command("hello nonexistent", "/current", lambda p, c: f"{c}/{p}", mock_parse_args)

                # Assert
                assert "ERROR: Путь не существует" in result
                mock_parse_args.assert_called_once_with("hello nonexistent")

    def test_grep_command_no_matches_found(self, mocker: MockerFixture):
        # Arrange
        mock_parse_args = mocker.Mock(return_value=([], ["nonexistent", "file.txt"]))

        with patch('commands.grep.pattern_search_path') as mock_pattern_path:
            mock_pattern_path.return_value = ("nonexistent", "/current/file.txt")
            with patch('commands.grep.validate_search_path') as mock_validate:
                mock_validate.return_value = (True, "/current/file.txt")
                with patch('commands.grep.compile_pattern') as mock_compile:
                    mock_pattern = Mock()
                    mock_compile.return_value = (True, mock_pattern)
                    with patch('commands.grep.files_search') as mock_files:
                        mock_file = Mock()
                        mock_files.return_value = (True, [mock_file])
                        with patch('commands.grep.perform_search') as mock_perform:
                            mock_perform.return_value = []

                            # Act
                            result = grep_command("nonexistent file.txt", "/current", lambda p, c: f"{c}/{p}", mock_parse_args)

                            # Assert
                            assert "Совпадений не найдено" in result
                            mock_parse_args.assert_called_once_with("nonexistent file.txt")

    def test_grep_command_permission_error(self, mocker: MockerFixture):
        # Arrange
        mock_parse_args = mocker.Mock(return_value=([], ["hello", "restricted"]))

        with patch('commands.grep.pattern_search_path') as mock_pattern_path:
            mock_pattern_path.return_value = ("hello", "/current/restricted")
            with patch('commands.grep.validate_search_path') as mock_validate:
                mock_validate.side_effect = PermissionError("Permission denied")

                # Act
                result = grep_command("hello restricted", "/current", lambda p, c: f"{c}/{p}", mock_parse_args)

                # Assert
                assert "ERROR: Ошибка прав доступа" in result
                mock_parse_args.assert_called_once_with("hello restricted")

if __name__ == '__main__':
    unittest.main()