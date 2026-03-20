"""
Image to Base64 converter module
Handles the conversion of image files to base64 strings
"""

import base64
import mimetypes
from pathlib import Path
from typing import Tuple, Optional


class ImageConverter:
    """Handles conversion of images to base64 format"""

    @staticmethod
    def image_to_base64(file_path: str) -> Tuple[str, str]:
        """
        Convert an image file to base64 string.

        Args:
            file_path: Path to the image file

        Returns:
            Tuple of (base64_string, mime_type)

        Raises:
            FileNotFoundError: If the file doesn't exist
            ValueError: If the file is not readable or not an image
        """
        path = Path(file_path)

        if not path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")

        if not path.is_file():
            raise ValueError(f"Not a file: {file_path}")

        # Try to determine MIME type
        mime_type, _ = mimetypes.guess_type(str(path))
        if not mime_type or not mime_type.startswith('image/'):
            # Default to octet-stream if we can't determine the type
            mime_type = 'application/octet-stream'

        # Read and encode the file
        try:
            with open(path, 'rb') as image_file:
                encoded_string = base64.b64encode(image_file.read()).decode('utf-8')
        except Exception as e:
            raise ValueError(f"Error reading file: {e}")

        return encoded_string, mime_type

    @staticmethod
    def image_to_data_uri(file_path: str) -> str:
        """
        Convert an image file to a data URI.

        Args:
            file_path: Path to the image file

        Returns:
            Data URI string in format: data:image/type;base64,xxxxx

        Raises:
            FileNotFoundError: If the file doesn't exist
            ValueError: If the file is not readable or not an image
        """
        base64_string, mime_type = ImageConverter.image_to_base64(file_path)
        return f"data:{mime_type};base64,{base64_string}"

    @staticmethod
    def get_file_info(file_path: str) -> dict:
        """
        Get information about an image file.

        Args:
            file_path: Path to the image file

        Returns:
            Dictionary with file information including:
            - name: filename
            - path: full path
            - size: size in bytes
            - size_formatted: human-readable size
            - mime_type: MIME type of the image
        """
        path = Path(file_path)

        if not path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")

        size = path.stat().st_size
        mime_type, _ = mimetypes.guess_type(str(path))

        # Format size in human-readable format
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size < 1024.0:
                size_formatted = f"{size:.1f} {unit}"
                break
            size /= 1024.0
        else:
            size_formatted = f"{size:.1f} TB"

        return {
            'name': path.name,
            'path': str(path.absolute()),
            'size': path.stat().st_size,
            'size_formatted': size_formatted,
            'mime_type': mime_type or 'application/octet-stream'
        }
