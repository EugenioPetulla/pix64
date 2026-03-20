#!/usr/bin/env python3
"""
Pix64 - Image to Base64 converter for GNOME
Main entry point for the application
"""

import sys
import gi

# Ensure GTK and Libadwaita are available
gi.require_version('Gtk', '4.0')
gi.require_version('Adw', '1')

from gi.repository import Gtk, Adw, Gio, GLib
from src.main_window import MainWindow


class Application(Adw.Application):
    """Main application class"""

    def __init__(self):
        super().__init__(
            application_id='com.github.pix64',
            flags=Gio.ApplicationFlags.FLAGS_NONE
        )

        # Add command line options if needed
        self.set_option_context_parameter_string("<image file>")

    def do_startup(self):
        """Called when the application starts"""
        Adw.Application.do_startup(self)

        # Create actions
        self._create_actions()

    def do_activate(self):
        """Called when the application is activated"""
        # Create main window
        win = MainWindow(application=self)

        # Store reference to main window for updates
        self.main_window = win

        # Show window
        win.present()

    def _create_actions(self):
        """Create application actions"""
        # Clear history action
        clear_history_action = Gio.SimpleAction.new('clear-history', None)
        clear_history_action.connect('activate', self._on_clear_history)
        self.add_action(clear_history_action)

    def _on_clear_history(self, action, param):
        """Handle clear history action"""
        from src.history_manager import HistoryManager
        history_manager = HistoryManager()

        # Clear all history
        if history_manager.clear_all_history():
            # Refresh history list in main window
            if hasattr(self, 'main_window'):
                self.main_window._refresh_history_list()
                self.main_window._show_toast("History cleared")
        else:
            # Show error toast
            if hasattr(self, 'main_window'):
                self.main_window._show_toast("Error clearing history")


def main(version):
    """Main entry point"""
    app = Application()
    return app.run(sys.argv)


if __name__ == '__main__':
    main('')
