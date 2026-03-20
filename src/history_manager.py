"""
History manager module
Handles the storage and retrieval of conversion history
"""

import json
import os
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Optional
from gi.repository import GLib


class HistoryManager:
    """Manages the history of image conversions"""

    def __init__(self, app_name: str = "pix64"):
        """
        Initialize the history manager.

        Args:
            app_name: Name of the application for data directory
        """
        self.app_name = app_name
        self.history_file = self._get_history_file_path()
        self.history: List[Dict] = []
        self._load_history()

    def _get_data_dir(self) -> Path:
        """
        Get the data directory path following XDG Base Directory Specification.

        Returns:
            Path to the application data directory
        """
        # Follow XDG Base Directory Specification
        data_home = os.environ.get('XDG_DATA_HOME')
        if data_home:
            base_dir = Path(data_home)
        else:
            base_dir = Path.home() / '.local' / 'share'

        app_dir = base_dir / self.app_name
        app_dir.mkdir(parents=True, exist_ok=True)

        return app_dir

    def _get_history_file_path(self) -> Path:
        """
        Get the path to the history file.

        Returns:
            Path to the history JSON file
        """
        return self._get_data_dir() / 'history.json'

    def _load_history(self) -> None:
        """Load history from the JSON file"""
        if self.history_file.exists():
            try:
                with open(self.history_file, 'r', encoding='utf-8') as f:
                    self.history = json.load(f)
            except (json.JSONDecodeError, IOError) as e:
                print(f"Error loading history: {e}")
                self.history = []
        else:
            self.history = []

    def _save_history(self) -> bool:
        """
        Save history to the JSON file.

        Returns:
            True if save was successful, False otherwise
        """
        try:
            with open(self.history_file, 'w', encoding='utf-8') as f:
                json.dump(self.history, f, indent=2, ensure_ascii=False)
            return True
        except IOError as e:
            print(f"Error saving history: {e}")
            return False

    def add_conversion(self, file_path: str, base64_string: str,
                       mime_type: str, file_size: int) -> Optional[Dict]:
        """
        Add a new conversion to the history.

        Args:
            file_path: Path to the original image file
            base64_string: The base64 encoded string
            mime_type: MIME type of the image
            file_size: Size of the original file in bytes

        Returns:
            The added conversion entry or None if failed
        """
        path = Path(file_path)

        entry = {
            'id': datetime.now().timestamp(),
            'timestamp': datetime.now().isoformat(),
            'file_name': path.name,
            'file_path': str(path.absolute()),
            'base64_string': base64_string,
            'mime_type': mime_type,
            'file_size': file_size,
            'base64_length': len(base64_string)
        }

        self.history.insert(0, entry)  # Add to beginning
        self.history = self.history[:100]  # Keep only last 100 entries

        if self._save_history():
            return entry
        return None

    def remove_conversion(self, conversion_id: float) -> bool:
        """
        Remove a conversion from the history.

        Args:
            conversion_id: ID of the conversion to remove

        Returns:
            True if removal was successful, False otherwise
        """
        initial_length = len(self.history)
        self.history = [h for h in self.history if h.get('id') != conversion_id]

        if len(self.history) < initial_length:
            return self._save_history()
        return False

    def clear_all_history(self) -> bool:
        """
        Clear all conversion history.

        Returns:
            True if clearing was successful, False otherwise
        """
        self.history = []
        return self._save_history()

    def get_all_history(self) -> List[Dict]:
        """
        Get all conversion history.

        Returns:
            List of all conversion entries
        """
        return self.history.copy()

    def get_conversion(self, conversion_id: float) -> Optional[Dict]:
        """
        Get a specific conversion by ID.

        Args:
            conversion_id: ID of the conversion to retrieve

        Returns:
            The conversion entry or None if not found
        """
        for entry in self.history:
            if entry.get('id') == conversion_id:
                return entry.copy()
        return None

    def get_history_count(self) -> int:
        """
        Get the number of items in history.

        Returns:
            Number of conversion entries
        """
        return len(self.history)

    def search_history(self, query: str) -> List[Dict]:
        """
        Search history by file name.

        Args:
            query: Search query string

        Returns:
            List of matching conversion entries
        """
        query_lower = query.lower()
        return [
            entry.copy() for entry in self.history
            if query_lower in entry.get('file_name', '').lower()
        ]

    def get_total_size(self) -> int:
        """
        Get total size of all original files in history.

        Returns:
            Total size in bytes
        """
        return sum(entry.get('file_size', 0) for entry in self.history)

    def format_timestamp(self, timestamp_str: str) -> str:
        """
        Format ISO timestamp to human-readable format.

        Args:
            timestamp_str: ISO format timestamp string

        Returns:
            Formatted timestamp string
        """
        try:
            dt = datetime.fromisoformat(timestamp_str)
            return dt.strftime('%d/%m/%Y %H:%M')
        except (ValueError, TypeError):
            return timestamp_str
