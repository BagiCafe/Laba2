from unittest.mock import patch
from pytest_mock import MockerFixture
import sys
import os
import unittest

# Добавляем пути для импорта
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
src_dir = os.path.join(parent_dir, 'src')
sys.path.insert(0, src_dir)

from commands.mv import mv_command


class TestMvCommand:  # Тесты для основной функции mv_command

    def test_mv_command_file_success(self, mocker: MockerFixture):
        # Arrange
        mock_parse_args = mocker.Mock(return_value=([], ["file1.txt", "file2.txt"]))

        with patch('commands.mv.source_destination_paths') as mock_paths:
            mock_paths.return_value = ("/current/file1.txt", "/current/file2.txt")
            with patch('commands.mv.validate_source_path') as mock_validate:
                mock_validate.return_value = (True, "/current/file1.txt")
                with patch('commands.mv.prepare_destination_path') as mock_prepare:
                    mock_prepare.return_value = "/current/file2.txt"
                    with patch('commands.mv.move_item') as mock_move:
                        mock_move.return_value = (True, "Перемещено: /current/file1.txt -> /current/file2.txt")

                        # Act
                        result = mv_command("file1.txt file2.txt", "/current", lambda p, c: f"{c}/{p}", mock_parse_args)

                        # Assert
                        assert "Перемещено" in result
                        mock_parse_args.assert_called_once_with("file1.txt file2.txt")

    def test_mv_command_directory_destination(self, mocker: MockerFixture):
        # Arrange
        mock_parse_args = mocker.Mock(return_value=([], ["file.txt", "destination_dir"]))

        with patch('commands.mv.source_destination_paths') as mock_paths:
            mock_paths.return_value = ("/current/file.txt", "/current/destination_dir")
            with patch('commands.mv.validate_source_path') as mock_validate:
                mock_validate.return_value = (True, "/current/file.txt")
                with patch('commands.mv.prepare_destination_path') as mock_prepare:
                    mock_prepare.return_value = "/current/destination_dir/file.txt"
                    with patch('commands.mv.move_item') as mock_move:
                        mock_move.return_value = (True, "Перемещено: /current/file.txt -> /current/destination_dir/file.txt")

                        # Act
                        result = mv_command("file.txt destination_dir", "/current", lambda p, c: f"{c}/{p}", mock_parse_args)

                        # Assert
                        assert "Перемещено" in result
                        assert "destination_dir/file.txt" in result
                        mock_parse_args.assert_called_once_with("file.txt destination_dir")

    def test_mv_command_nonexistent_source(self, mocker: MockerFixture):
        # Arrange
        mock_parse_args = mocker.Mock(return_value=([], ["nonexistent.txt", "destination.txt"]))

        with patch('commands.mv.source_destination_paths') as mock_paths:
            mock_paths.return_value = ("/current/nonexistent.txt", "/current/destination.txt")
            with patch('commands.mv.validate_source_path') as mock_validate:
                mock_validate.return_value = (False, "ERROR: Источник не существует: /current/nonexistent.txt")

                # Act
                result = mv_command("nonexistent.txt destination.txt", "/current", lambda p, c: f"{c}/{p}", mock_parse_args)

                # Assert
                assert "ERROR: Источник не существует" in result
                mock_parse_args.assert_called_once_with("nonexistent.txt destination.txt")

    def test_mv_command_insufficient_parameters(self, mocker: MockerFixture):
        # Arrange
        mock_parse_args = mocker.Mock(return_value=([], ["file1.txt"]))

        with patch('commands.mv.source_destination_paths') as mock_paths:
            mock_paths.return_value = ("/current/file1.txt", "")

            # Act
            result = mv_command("file1.txt", "/current", lambda p, c: f"{c}/{p}", mock_parse_args)

            # Assert
            assert "ERROR: Необходимо указать источник и назначение" in result
            mock_parse_args.assert_called_once_with("file1.txt")

    def test_mv_command_move_error(self, mocker: MockerFixture):
        # Arrange
        mock_parse_args = mocker.Mock(return_value=([], ["file1.txt", "file2.txt"]))

        with patch('commands.mv.source_destination_paths') as mock_paths:
            mock_paths.return_value = ("/current/file1.txt", "/current/file2.txt")
            with patch('commands.mv.validate_source_path') as mock_validate:
                mock_validate.return_value = (True, "/current/file1.txt")
                with patch('commands.mv.prepare_destination_path') as mock_prepare:
                    mock_prepare.return_value = "/current/file2.txt"
                    with patch('commands.mv.move_item') as mock_move:
                        mock_move.return_value = (False, "ERROR: Ошибка перемещения: Permission denied")

                        # Act
                        result = mv_command("file1.txt file2.txt", "/current", lambda p, c: f"{c}/{p}", mock_parse_args)

                        # Assert
                        assert "ERROR: Ошибка перемещения" in result
                        mock_parse_args.assert_called_once_with("file1.txt file2.txt")

    def test_mv_command_permission_error(self, mocker: MockerFixture):
        # Arrange
        mock_parse_args = mocker.Mock(return_value=([], ["file1.txt", "file2.txt"]))

        with patch('commands.mv.source_destination_paths') as mock_paths:
            mock_paths.return_value = ("/current/file1.txt", "/current/file2.txt")
            with patch('commands.mv.validate_source_path') as mock_validate:
                mock_validate.side_effect = PermissionError("Permission denied")

                # Act
                result = mv_command("file1.txt file2.txt", "/current", lambda p, c: f"{c}/{p}", mock_parse_args)

                # Assert
                assert "ERROR: Ошибка прав доступа" in result
                mock_parse_args.assert_called_once_with("file1.txt file2.txt")

    def test_mv_command_general_exception(self, mocker: MockerFixture):
        # Arrange
        mock_parse_args = mocker.Mock(return_value=([], ["file1.txt", "file2.txt"]))

        with patch('commands.mv.source_destination_paths') as mock_paths:
            mock_paths.return_value = ("/current/file1.txt", "/current/file2.txt")
            with patch('commands.mv.validate_source_path') as mock_validate:
                mock_validate.side_effect = Exception("Unexpected error")

                # Act
                result = mv_command("file1.txt file2.txt", "/current", lambda p, c: f"{c}/{p}", mock_parse_args)

                # Assert
                assert "ERROR: Unexpected error" in result
                mock_parse_args.assert_called_once_with("file1.txt file2.txt")

if __name__ == '__main__':
    unittest.main()