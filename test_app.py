"""Unit tests. They replace the database with a fake, so no MySQL is needed to run them."""
import unittest
from unittest.mock import MagicMock, patch

import pymysql

import app as notes_app


def fake_connection(rows=None):
    """Build a fake database connection whose cursor returns `rows`."""
    cursor = MagicMock()
    cursor.fetchall.return_value = rows or []
    connection = MagicMock()
    connection.cursor.return_value.__enter__.return_value = cursor
    return connection, cursor


class NotesAppTests(unittest.TestCase):
    def setUp(self):
        notes_app.app.testing = True
        self.client = notes_app.app.test_client()

    @patch("app.get_connection")
    def test_health_ok_when_database_is_up(self, mock_get_connection):
        mock_get_connection.return_value, _ = fake_connection()
        response = self.client.get("/health")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json()["database"], "up")

    @patch("app.get_connection", side_effect=pymysql.err.OperationalError(2003, "down"))
    def test_health_is_503_when_database_is_down(self, _mock_get_connection):
        response = self.client.get("/health")
        self.assertEqual(response.status_code, 503)
        self.assertEqual(response.get_json()["database"], "down")

    @patch("app.ensure_schema")
    @patch("app.get_connection")
    def test_home_page_shows_a_note(self, mock_get_connection, _mock_schema):
        from datetime import datetime

        row = {"id": 1, "author": "Asha", "content": "Hello world", "created_at": datetime(2026, 1, 2, 3, 4)}
        mock_get_connection.return_value, _ = fake_connection([row])
        response = self.client.get("/")
        self.assertEqual(response.status_code, 200)
        self.assertIn(b"Hello world", response.data)

    @patch("app.ensure_schema")
    @patch("app.get_connection")
    def test_note_text_is_escaped(self, mock_get_connection, _mock_schema):
        from datetime import datetime

        row = {"id": 1, "author": "x", "content": "<script>alert(1)</script>", "created_at": datetime(2026, 1, 2, 3, 4)}
        mock_get_connection.return_value, _ = fake_connection([row])
        response = self.client.get("/")
        self.assertNotIn(b"<script>alert(1)</script>", response.data)

    @patch("app.get_connection")
    def test_empty_note_is_not_saved(self, mock_get_connection):
        response = self.client.post("/notes", data={"author": "Asha", "content": "   "})
        self.assertEqual(response.status_code, 302)
        mock_get_connection.assert_not_called()

    @patch("app.ensure_schema")
    @patch("app.get_connection")
    def test_valid_note_is_inserted(self, mock_get_connection, _mock_schema):
        connection, cursor = fake_connection()
        mock_get_connection.return_value = connection
        response = self.client.post("/notes", data={"author": "Asha", "content": "Hi"})
        self.assertEqual(response.status_code, 302)
        cursor.execute.assert_called_once()
        self.assertEqual(cursor.execute.call_args[0][1], ("Asha", "Hi"))


if __name__ == "__main__":
    unittest.main()