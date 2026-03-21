"""
Main window module
Contains the GTK4/Libadwaita user interface
"""

from gi.repository import Gtk, Adw, Gdk, GLib, Gio, GObject
from pathlib import Path
from .image_converter import ImageConverter
from .history_manager import HistoryManager
from typing import Optional
import threading


class MainWindow(Adw.ApplicationWindow):
    """Main application window"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Initialize managers
        self.history_manager = HistoryManager()
        self.current_conversion = None

        # Window setup
        self.set_title("Pix64")
        self.set_default_size(900, 650)
        self.set_size_request(600, 400)

        # Load CSS
        self._load_css()

        # Build UI
        self._build_ui()

        # Load history
        self._refresh_history_list()

    def _load_css(self):
        """Load custom CSS styling"""
        provider = Gtk.CssProvider()
        css_file = Path(__file__).parent.parent / "data" / "style.css"

        if css_file.exists():
            try:
                provider.load_from_path(str(css_file))
            except Exception as e:
                print(f"Error loading CSS: {e}")
                return
        else:
            # Inline CSS if file doesn't exist
            css = b"""
                .drop-area {
                    border: 2px dashed @borders;
                    border-radius: 12px;
                    padding: 40px;
                    background: alpha(@view_bg_color, 0.5);
                }

                .drop-area:hover {
                    border-color: @accent_color;
                    background: alpha(@accent_bg_color, 0.1);
                }

                .main-content {
                    padding: 24px;
                }

                .history-item {
                    padding: 12px;
                    border-radius: 8px;
                    margin: 4px 0;
                }

                .base64-text {
                    font-family: monospace;
                    font-size: 11px;
                }

                .title-label {
                    font-size: 24px;
                    font-weight: bold;
                }

                .subtitle-label {
                    font-size: 14px;
                    color: @window_fg_color;
                    opacity: 0.7;
                }

                .copy-button {
                    padding: 12px 24px;
                }

                .image-preview {
                    border-radius: 8px;
                }
            """
            provider.load_from_data(css)

        Gtk.StyleContext.add_provider_for_display(
            self.get_display(), provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
        )

    def _build_ui(self):
        """Build the main user interface"""
        # Create split view first (needed for header bar binding)
        self.split_view = Adw.OverlaySplitView()
        self.split_view.set_min_sidebar_width(280)
        self.split_view.set_max_sidebar_width(400)
        self.split_view.set_sidebar_width_fraction(0.3)

        # Main container
        main_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)

        # Header bar
        self._build_header_bar(main_box)

        # Main content with toolbar view
        toolbar_view = Adw.ToolbarView()
        main_box.append(toolbar_view)

        toolbar_view.set_content(self.split_view)

        # Create ToastOverlay for notifications
        self.toast_overlay = Adw.ToastOverlay()
        self.toast_overlay.set_child(main_box)

        # Set ToastOverlay as window content
        self.set_content(self.toast_overlay)

        # Sidebar (History)
        self._build_sidebar()

        # Main content
        self._build_main_content()

    def _build_header_bar(self, parent):
        """Build the header bar"""
        header_bar = Adw.HeaderBar()
        header_bar.add_css_class("flat")
        parent.append(header_bar)

        # Open image button
        open_button = Gtk.Button(icon_name="document-open-symbolic")
        open_button.set_tooltip_text("Open Image")
        open_button.connect("clicked", self._on_open_clicked)
        header_bar.pack_start(open_button)

        # Toggle history sidebar button
        history_button = Gtk.ToggleButton(icon_name="sidebar-show-symbolic")
        history_button.set_tooltip_text("Toggle History")
        history_button.bind_property(
            "active",
            self.split_view,
            "show-sidebar",
            GObject.BindingFlags.BIDIRECTIONAL,
        )
        header_bar.pack_end(history_button)

        # Clear history button (only in menu)
        menu = Gio.Menu.new()
        menu.append("Clear History", "app.clear-history")

        menu_button = Gtk.MenuButton(icon_name="open-menu-symbolic")
        menu_button.set_menu_model(menu)
        header_bar.pack_end(menu_button)

    def _build_sidebar(self):
        """Build the history sidebar"""
        # Sidebar content
        sidebar_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        sidebar_box.add_css_class("background")

        # Sidebar header
        sidebar_header = Adw.HeaderBar()
        sidebar_header.add_css_class("flat")
        sidebar_header.set_title_widget(Gtk.Label(label="History"))
        sidebar_box.append(sidebar_header)

        # Scrolled window for history list
        scrolled = Gtk.ScrolledWindow()
        scrolled.set_hexpand(True)
        scrolled.set_vexpand(True)
        scrolled.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)

        # History list box
        self.history_list = Gtk.ListBox()
        self.history_list.add_css_class("background")
        self.history_list.set_selection_mode(Gtk.SelectionMode.SINGLE)
        self.history_list.connect("row-activated", self._on_history_row_activated)
        scrolled.set_child(self.history_list)

        sidebar_box.append(scrolled)

        # Set sidebar
        self.split_view.set_sidebar(sidebar_box)

    def _build_main_content(self):
        """Build the main content area"""
        # Main content box
        content_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        content_box.add_css_class("main-content")
        content_box.set_spacing(24)

        # Drop area
        self.drop_frame = Gtk.Frame()
        self.drop_frame.add_css_class("drop-area")

        drop_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        drop_box.set_spacing(16)
        drop_box.set_halign(Gtk.Align.CENTER)
        drop_box.set_valign(Gtk.Align.CENTER)

        self.loading_spinner = Gtk.Spinner()
        self.loading_spinner.set_visible(False)
        drop_box.append(self.loading_spinner)

        # Icon
        icon = Gtk.Image(icon_name="image-x-generic-symbolic")
        icon.set_pixel_size(64)
        drop_box.append(icon)

        # Title
        title_label = Gtk.Label(label="Drop an image here")
        title_label.add_css_class("title-label")
        drop_box.append(title_label)

        # Subtitle
        subtitle_label = Gtk.Label(label="or click to select a file")
        subtitle_label.add_css_class("subtitle-label")
        drop_box.append(subtitle_label)

        # Select button
        select_button = Gtk.Button(label="Select Image")
        select_button.add_css_class("pill")
        select_button.add_css_class("suggested-action")
        select_button.connect("clicked", self._on_open_clicked)
        drop_box.append(select_button)

        self.drop_frame.set_child(drop_box)
        content_box.append(self.drop_frame)

        # Setup drag and drop
        self._setup_drag_drop(self.drop_frame)

        # Results section (initially hidden)
        self.results_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        self.results_box.add_css_class("card")
        self.results_box.set_spacing(16)
        self.results_box.set_visible(False)

        # Image preview
        preview_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        preview_box.set_spacing(16)

        self.image_preview = Gtk.Image()
        self.image_preview.set_pixel_size(128)
        self.image_preview.add_css_class("image-preview")
        preview_box.append(self.image_preview)

        # File info
        info_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        info_box.set_spacing(4)
        info_box.set_hexpand(True)
        info_box.set_valign(Gtk.Align.CENTER)

        self.file_name_label = Gtk.Label()
        self.file_name_label.add_css_class("heading")
        self.file_name_label.set_halign(Gtk.Align.START)
        info_box.append(self.file_name_label)

        self.file_info_label = Gtk.Label()
        self.file_info_label.add_css_class("caption")
        self.file_info_label.set_halign(Gtk.Align.START)
        info_box.append(self.file_info_label)

        preview_box.append(info_box)

        self.results_box.append(preview_box)

        # Base64 output section
        output_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        output_box.set_spacing(8)

        output_label = Gtk.Label(label="Base64 Output")
        output_label.add_css_class("heading")
        output_label.set_halign(Gtk.Align.START)
        output_box.append(output_label)

        # Scrolled window for base64 text
        scrolled_output = Gtk.ScrolledWindow()
        scrolled_output.set_policy(Gtk.PolicyType.AUTOMATIC, Gtk.PolicyType.AUTOMATIC)
        scrolled_output.set_min_content_height(150)

        self.base64_textview = Gtk.TextView()
        self.base64_textview.add_css_class("base64-text")
        self.base64_textview.set_editable(False)
        self.base64_textview.set_wrap_mode(Gtk.WrapMode.CHAR)
        scrolled_output.set_child(self.base64_textview)

        output_box.append(scrolled_output)

        # Action buttons
        button_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL)
        button_box.set_spacing(12)
        button_box.set_halign(Gtk.Align.END)

        copy_base64_button = Gtk.Button(label="Copy Base64")
        copy_base64_button.add_css_class("copy-button")
        copy_base64_button.add_css_class("suggested-action")
        copy_base64_button.connect("clicked", self._on_copy_base64)
        button_box.append(copy_base64_button)

        copy_uri_button = Gtk.Button(label="Copy Data URI")
        copy_uri_button.add_css_class("copy-button")
        copy_uri_button.connect("clicked", self._on_copy_data_uri)
        button_box.append(copy_uri_button)

        output_box.append(button_box)

        self.results_box.append(output_box)

        content_box.append(self.results_box)

        # Set content
        self.split_view.set_content(content_box)

    def _setup_drag_drop(self, widget):
        """Setup drag and drop for the widget"""
        target = Gtk.DropTarget.new(Gdk.FileList, Gdk.DragAction.COPY)
        target.connect("drop", self._on_file_drop)
        widget.add_controller(target)

    def _on_file_drop(self, target, value, x, y):
        """Handle file drop"""
        if isinstance(value, Gdk.FileList):
            files = value.get_files()
            if files:
                file = files[0]
                file_path = file.get_path()
                if file_path:
                    self._load_image(file_path)
                    return True
        return False

    def _on_open_clicked(self, button):
        """Handle open button click"""
        filter = Gtk.FileFilter()
        filter.set_name("Image files")
        filter.add_mime_type("image/*")
        filter.add_pattern("*.png")
        filter.add_pattern("*.jpg")
        filter.add_pattern("*.jpeg")
        filter.add_pattern("*.gif")
        filter.add_pattern("*.webp")
        filter.add_pattern("*.svg")

        dialog = Gtk.FileDialog()
        dialog.set_title("Select an Image")
        dialog.set_filters(Gio.ListStore.new(Gtk.FileFilter))
        dialog.get_filters().append(filter)

        dialog.open(self, None, self._on_file_dialog_response)

    def _on_file_dialog_response(self, dialog, result):
        """Handle file dialog response"""
        try:
            file = dialog.open_finish(result)
            if file:
                file_path = file.get_path()
                if file_path:
                    self._load_image(file_path)
        except GLib.Error as e:
            if e.code != Gtk.DialogError.FAILED:
                print(f"Error selecting file: {e.message}")

    def _load_image(self, file_path):
        """Load and convert an image in a background thread"""
        self._show_loading(True)

        def convert_in_thread():
            try:
                file_info = ImageConverter.get_file_info(file_path)
                base64_string, mime_type = ImageConverter.image_to_base64(file_path)

                GLib.idle_add(
                    self._on_conversion_complete,
                    file_path,
                    base64_string,
                    mime_type,
                    file_info,
                    None,
                )
            except Exception as e:
                GLib.idle_add(
                    self._on_conversion_complete, None, None, None, None, str(e)
                )

        thread = threading.Thread(target=convert_in_thread, daemon=True)
        thread.start()

    def _on_conversion_complete(
        self, file_path, base64_string, mime_type, file_info, error
    ):
        """Handle conversion completion on main thread"""
        self._show_loading(False)

        if error:
            self._show_error(error)
            return

        entry = self.history_manager.add_conversion(
            file_path, base64_string, mime_type, file_info["size"]
        )

        self.current_conversion = entry
        self._update_results(file_path, base64_string, mime_type, file_info)
        self._refresh_history_list()

    def _show_loading(self, loading):
        """Show or hide loading indicator"""
        if hasattr(self, "loading_spinner"):
            self.loading_spinner.set_spinning(loading)
            self.loading_spinner.set_visible(loading)
        if hasattr(self, "drop_frame"):
            self.drop_frame.set_sensitive(not loading)

    def _update_results(self, file_path, base64_string, mime_type, file_info):
        """Update the results display"""
        self.results_box.set_visible(True)

        try:
            texture = Gdk.Texture.new_from_filename(file_path)
            self.image_preview.set_paintable(texture)
        except Exception:
            self.image_preview.set_from_icon_name("image-missing-symbolic")

        self.file_name_label.set_text(file_info["name"])
        self.file_info_label.set_text(
            f"{file_info['size_formatted']} • {mime_type} • {len(base64_string)} chars"
        )

        buffer = self.base64_textview.get_buffer()
        max_display_chars = 50000
        if len(base64_string) > max_display_chars:
            truncated = (
                base64_string[:max_display_chars]
                + f"\n\n... (truncated, {len(base64_string) - max_display_chars:,} more characters - use Copy buttons for full string)"
            )
            buffer.set_text(truncated)
        else:
            buffer.set_text(base64_string)

        start_iter = buffer.get_start_iter()
        buffer.place_cursor(start_iter)
        insert_mark = buffer.get_insert()
        self.base64_textview.scroll_mark_onscreen(insert_mark)

    def _on_copy_base64(self, button):
        """Copy base64 string to clipboard"""
        if self.current_conversion and "base64_string" in self.current_conversion:
            self._copy_to_clipboard(self.current_conversion["base64_string"])
            self._show_toast("Base64 string copied!")

    def _on_copy_data_uri(self, button):
        """Copy data URI to clipboard"""
        if self.current_conversion:
            data_uri = f"data:{self.current_conversion['mime_type']};base64,{self.current_conversion['base64_string']}"
            self._copy_to_clipboard(data_uri)
            self._show_toast("Data URI copied!")

    def _copy_to_clipboard(self, text):
        """Copy text to clipboard"""
        display = Gdk.Display.get_default()
        if display:
            clipboard = display.get_clipboard()
            clipboard.set_content(Gdk.ContentProvider.new_for_value(text))

    def _show_toast(self, message):
        """Show a toast notification"""
        toast = Adw.Toast.new(message)
        toast.set_timeout(2)

        # Use the internal ToastOverlay
        if hasattr(self, "toast_overlay"):
            self.toast_overlay.add_toast(toast)
        else:
            print(f"Toast: {message}")

    def _show_error(self, message):
        """Show an error dialog"""
        dialog = Adw.AlertDialog.new("Error", message)
        dialog.add_response("ok", "OK")
        dialog.present(self)

    def _refresh_history_list(self):
        """Refresh the history list"""
        # Clear existing items
        while child := self.history_list.get_first_child():
            self.history_list.remove(child)

        # Add history items
        history = self.history_manager.get_all_history()

        if not history:
            # Show empty state
            empty_label = Gtk.Label(label="No conversions yet")
            empty_label.add_css_class("dim-label")
            empty_label.set_margin_top(12)
            empty_label.set_margin_bottom(12)
            self.history_list.append(empty_label)
            return

        for entry in history:
            row = self._create_history_row(entry)
            self.history_list.append(row)

    def _create_history_row(self, entry):
        """Create a history list row"""
        row = Gtk.ListBoxRow()
        row.add_css_class("history-item")

        box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL)
        box.set_spacing(4)

        # File name
        name_label = Gtk.Label(label=entry.get("file_name", "Unknown"))
        name_label.add_css_class("heading")
        name_label.set_halign(Gtk.Align.START)
        name_label.set_ellipsize(True)
        box.append(name_label)

        # Timestamp
        timestamp = self.history_manager.format_timestamp(entry.get("timestamp", ""))
        time_label = Gtk.Label(label=timestamp)
        time_label.add_css_class("caption")
        time_label.set_halign(Gtk.Align.START)
        box.append(time_label)

        # File size
        size = entry.get("file_size", 0)
        size_str = f"{size / 1024:.1f} KB"
        size_label = Gtk.Label(label=size_str)
        size_label.add_css_class("caption")
        size_label.set_halign(Gtk.Align.START)
        box.append(size_label)

        # Store entry data in row
        row.conversion_id = entry.get("id")

        row.set_child(box)
        return row

    def _on_history_row_activated(self, list_box, row):
        """Handle history row activation"""
        if hasattr(row, "conversion_id"):
            entry = self.history_manager.get_conversion(row.conversion_id)
            if entry:
                self.current_conversion = entry

                # Update UI with selected conversion
                self._update_results(
                    entry.get("file_path", ""),
                    entry.get("base64_string", ""),
                    entry.get("mime_type", ""),
                    {
                        "name": entry.get("file_name", "Unknown"),
                        "size_formatted": f"{entry.get('file_size', 0) / 1024:.1f} KB",
                        "size": entry.get("file_size", 0),
                    },
                )
