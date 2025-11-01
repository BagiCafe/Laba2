import sys
import os
from unittest.mock import Mock, patch
from pytest_mock import MockerFixture
import unittest

# Добавляем путь к src для корректного импорта
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
src_dir = os.path.join(parent_dir, 'src')
sys.path.insert(0, src_dir)

from commands.ls import ls_command, files_list, simple_output, process_arguments


class TestLsCommand:  # Тесты для основной функции ls_command

    def test_ls_command_nonexistent_path(self, mocker: MockerFixture):
        # Arrange
        mock_get_absolute_path = mocker.Mock(return_value="/nonexistent")
        mock_parse_args = mocker.Mock(return_value=([], ["/nonexistent"]))

        # Мокаем Path
        mock_path = mocker.Mock()
        mock_path.exists.return_value = False

        with patch('commands.ls.Path', return_value=mock_path):
            # Act
            result = ls_command("/nonexistent", "/current", mock_get_absolute_path, mock_parse_args)

            # Assert
            assert result == "ERROR: Такого файла или каталога нет"
            mock_get_absolute_path.assert_called_once_with("/nonexistent", "/current")
            mock_parse_args.assert_called_once_with("/nonexistent")

    def test_ls_command_simple_output_directory(self, mocker: MockerFixture):
        # Arrange
        mock_get_absolute_path = mocker.Mock(return_value="/test")
        mock_parse_args = mocker.Mock(return_value=([], ["/test"]))

        mock_file1 = mocker.Mock()
        mock_file1.name = "гусь1.txt"
        mock_file2 = mocker.Mock()
        mock_file2.name = "гусь1.py"

        mock_path = mocker.Mock()
        mock_path.exists.return_value = True
        mock_path.is_file.return_value = False
        mock_path.iterdir.return_value = [mock_file1, mock_file2]

        with patch('commands.ls.Path', return_value=mock_path):
            # Act
            result = ls_command("/test", "/current", mock_get_absolute_path, mock_parse_args)

            # Assert
            assert "гусь1.txt" in result
            assert "гусь1.py" in result
            mock_get_absolute_path.assert_called_once_with("/test", "/current")
            mock_parse_args.assert_called_once_with("/test")

    def test_ls_command_current_directory(self, mocker: MockerFixture):
        # Arrange
        mock_get_absolute_path = mocker.Mock(return_value="/current")
        mock_parse_args = mocker.Mock(return_value=([], []))

        mock_file1 = mocker.Mock()
        mock_file1.name = "гусь1.txt"

        mock_path = mocker.Mock()
        mock_path.exists.return_value = True
        mock_path.is_file.return_value = False
        mock_path.iterdir.return_value = [mock_file1]

        with patch('commands.ls.Path', return_value=mock_path):
            # Act
            result = ls_command("", "/current", mock_get_absolute_path, mock_parse_args)

            # Assert
            assert "гусь1.txt" in result
            mock_get_absolute_path.assert_called_once_with("/current", "/current")
            mock_parse_args.assert_called_once_with("")


class TestFilesList:  # Тесты для функции files_list
    def test_files_list_directory(self):
        # Arrange
        mock_path = Mock()
        mock_path.is_file.return_value = False
        mock_file1 = Mock()
        mock_file2 = Mock()
        mock_path.iterdir.return_value = [mock_file1, mock_file2]

        # Act
        result = files_list(mock_path)

        # Assert
        assert result == [mock_file1, mock_file2]
        mock_path.is_file.assert_called_once()
        mock_path.iterdir.assert_called_once()

    def test_files_list_single_file(self):
        # Arrange
        mock_path = Mock()
        mock_path.is_file.return_value = True

        # Act
        result = files_list(mock_path)

        # Assert
        assert result == [mock_path]
        mock_path.is_file.assert_called_once()


class TestOutputFunctions:  # Тесты для функций вывода

    def test_simple_output(self):
        # Arrange
        mock_file1 = Mock()
        mock_file1.name = "гусь1.txt"
        mock_file2 = Mock()
        mock_file2.name = "гусь2.py"
        files = [mock_file1, mock_file2]

        # Act
        result = simple_output(files)

        # Assert
        assert result == "гусь1.txt  гусь2.py"


class TestProcessArguments: # Тесты для функции process_arguments

    def test_process_arguments_with_path(self):
        # Arrange
        mock_get_absolute_path = Mock(return_value="/absolute/path/гусь")
        mock_parse_args = Mock(return_value=(["-l"], ["relative/path"]))

        # Act
        target, flags, parameters = process_arguments(
            "-l relative/path", "/current", mock_get_absolute_path, mock_parse_args
        )

        # Assert
        assert flags == ["-l"]
        assert parameters == ["relative/path"]
        mock_parse_args.assert_called_once_with("-l relative/path")
        mock_get_absolute_path.assert_called_once_with("relative/path", "/current")

if __name__ == '__main__':
    unittest.main()