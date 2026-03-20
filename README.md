# Pix64

<div align="center">  
  **A minimal and elegant image to Base64 converter for GNOME**
  
  [![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)](https://www.gnu.org/licenses/gpl-3.0)
  [![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)](https://www.python.org)
</div>

---

## 📖 Description

Pix64 is a modern, minimal application for converting images to Base64 strings, designed specifically for the GNOME desktop environment. With a clean and intuitive interface following the GNOME Human Interface Guidelines, Pix64 makes it easy to encode images and copy the resulting strings with a single click.

## ✨ Features

- **🖼️ Image to Base64 Conversion**: Convert any image format to Base64 string
- **📋 One-Click Copy**: Copy Base64 strings or Data URIs instantly
- **📚 Conversion History**: Keep track of all your conversions with automatic saving
- **🗑️ History Management**: Clear individual items or entire history
- **🎨 GNOME Integration**: Native look and feel with Libadwaita
- **🖱️ Drag & Drop**: Simply drag images onto the window to convert
- **   Dark Mode**: Automatic support for dark/light themes
- **💾 Persistent Storage**: History saved locally for future sessions
- **   Fast & Lightweight**: Minimal resource usage


## 🔧 Requirements

- **Operating System**: Linux (GNOME Desktop recommended)
- **Python**: 3.9 or higher
- **GTK**: 4.0 or higher
- **Libadwaita**: 1.0 or higher
- **PyGObject**: 3.42.0 or higher

### Runtime Dependencies

Make sure you have the following packages installed on your system:

#### Fedora/RHEL
```bash
sudo dnf install python3-gobject gtk4 libadwaita
```

#### Ubuntu/Debian
```bash
sudo apt install python3-gi gtk4 libadwaita-1-0
```

#### Arch Linux
```bash
sudo pacman -S python-gobject gtk4 libadwaita
```

#### openSUSE
```bash
sudo zypper install python3-gobject gtk4 libadwaita
```

## 📥 Installation

### From Source

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/pix64.git
   cd pix64
   ```

2. **Install Python dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the application**
   ```bash
   python main.py
   ```

## 🚀 Usage

### Basic Usage

1. **Launch Pix64** by running `python main.py` or clicking the application icon
2. **Select an image** using one of these methods:
   - Click the "Select Image" button
   - Click the "Open" button in the header bar
   - Drag and drop an image file onto the window
3. **View the conversion** - The Base64 string will appear in the results area
4. **Copy the result**:
   - Click "Copy Base64" to copy just the Base64 string
   - Click "Copy Data URI" to copy the complete data URI with MIME type

### Using History

- Click the **sidebar toggle button** in the header bar to show/hide history
- Click on any previous conversion to view it again
- Previous conversions are automatically saved and persist across sessions

### Clearing History

- Click the **menu button** (three dots) in the header bar
- Select **"Clear History"** to remove all saved conversions

## 🎨 Supported Image Formats

Pix64 supports all common image formats, including:

- PNG (`.png`)
- JPEG (`.jpg`, `.jpeg`)
- GIF (`.gif`)
- WebP (`.webp`)
- SVG (`.svg`)
- BMP (`.bmp`)
- TIFF (`.tiff`, `.tif`)
- And many more...

## Key Components

### ImageConverter
Handles the conversion of image files to Base64 strings and data URIs.

### HistoryManager
Manages the persistent storage of conversion history using JSON files stored in `~/.local/share/pix64/`.

### MainWindow
The main GTK4/Libadwaita interface providing the user interface and user interactions.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request. For major changes, please open an issue first to discuss what you would like to change.

### Development Setup

1. Fork and clone the repository
2. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Make your changes and test thoroughly
5. Submit a pull request

### Coding Standards

- Follow PEP 8 style guidelines
- Add docstrings to all functions and classes
- Keep functions focused and concise
- Test on both light and dark themes

## License

This project is licensed under the GNU General Public License v3.0 - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- [GNOME Project](https://www.gnome.org/) for the amazing GTK and Libadwaita libraries
- [Python Software Foundation](https://www.python.org/) for Python
- All contributors and users of Pix64

## Contact

- **Issues**: Please use the [GitHub issue tracker](https://github.com/yourusername/pix64/issues)
- **Feature Requests**: Open an issue with the "enhancement" label
