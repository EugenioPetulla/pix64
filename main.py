#!/usr/bin/env python3
"""
Pix64 - Image to Base64 converter for GNOME
Main entry point for the application
"""

import sys
import gi

# Ensure GTK and Libadwaita are available
gi.require_version("Gtk", "4.0")
gi.require_version("Adw", "1")

from gi.repository import Gtk, Adw, Gio, GLib
from src.main_window import MainWindow


class Application(Adw.Application):
    """Main application class"""

    def __init__(self):
        super().__init__(
            application_id="com.github.pix64", flags=Gio.ApplicationFlags.FLAGS_NONE
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
        clear_history_action = Gio.SimpleAction.new("clear-history", None)
        clear_history_action.connect("activate", self._on_clear_history)
        self.add_action(clear_history_action)

        # Delete single history item action
        delete_item_action = Gio.SimpleAction.new("delete-history-item", None)
        delete_item_action.connect("activate", self._on_delete_history_item)
        self.add_action(delete_item_action)

    def _on_clear_history(self, action, param):
        """Handle clear history action"""
        if hasattr(self, "main_window") and self.main_window:
            if self.main_window.history_manager.clear_all_history():
                self.main_window._refresh_history_list()
                self.main_window._show_toast("History cleared")
            else:
                self.main_window._show_toast("Error clearing history")

    def _on_delete_history_item(self, action, param):
        """Handle delete single history item action"""
        if hasattr(self, "main_window") and self.main_window:
            if hasattr(self.main_window, "_pending_delete_id"):
                item_id = self.main_window._pending_delete_id
                if self.main_window.history_manager.remove_conversion(item_id):
                    self.main_window._refresh_history_list()
                    self.main_window._show_toast("Item deleted")
                else:
                    self.main_window._show_toast("Error deleting item")


def main(version):
    """Main entry point"""
    app = Application()
    return app.run(sys.argv)


if __name__ == "__main__":
    main("")
