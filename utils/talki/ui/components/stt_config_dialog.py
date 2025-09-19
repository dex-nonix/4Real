"""
STTConfigDialog - Dialog for managing STT configurations.
"""

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QListWidget, QListWidgetItem,
    QPushButton, QSplitter, QMessageBox, QInputDialog, QComboBox
)
from PyQt6.QtCore import pyqtSignal
from PyQt6.QtGui import QFont
from talki.config.logging_config import logger
from talki.core.stt_engine import STTConfig
from talki.services.config_manager import ConfigManager
from .stt_config_editor import STTConfigEditor


class STTConfigDialog(QDialog):
    """
    Dialog for managing STT configurations.
    """

    # Signals
    config_saved = pyqtSignal(STTConfig)  # Emitted when config is saved
    config_selected = pyqtSignal(str)     # Emitted when config is selected to use

    def __init__(self, config_manager: ConfigManager, parent=None):
        """Initialize config dialog."""
        super().__init__(parent)

        self.config_manager = config_manager

        # UI Elements
        self.config_list = None
        self.config_editor = None
        self.current_config_name = None

        self.setWindowTitle("STT Configuration Manager")
        self.setMinimumSize(800, 600)
        self.resize(1000, 700)

        self._create_ui()
        self._setup_layout()
        self._populate_config_list()

        logger.debug("🗣️  STTConfigDialog initialized")

    def _create_ui(self):
        """Create all UI elements."""
        # Config list
        self.config_list = QListWidget()
        self.config_list.currentItemChanged.connect(self._on_config_selected)

        # Config editor
        self.config_editor = STTConfigEditor()
        self.config_editor.config_changed.connect(self._on_config_changed)
        self.config_editor.save_requested.connect(self._on_save_requested)
        self.config_editor.cancel_requested.connect(self._on_cancel_requested)

        # Buttons
        self.new_button = QPushButton("🆕 New")
        self.new_button.clicked.connect(self._on_new_clicked)

        self.duplicate_button = QPushButton("📋 Duplicate")
        self.duplicate_button.clicked.connect(self._on_duplicate_clicked)

        self.delete_button = QPushButton("🗑️  Delete")
        self.delete_button.clicked.connect(self._on_delete_clicked)

        self.use_button = QPushButton("✅ Use This Config")
        self.use_button.clicked.connect(self._on_use_clicked)
        self.use_button.setEnabled(False)

        self.close_button = QPushButton("❌ Close")
        self.close_button.clicked.connect(self._on_close_clicked)

    def _setup_layout(self):
        """Set up the dialog layout."""
        main_layout = QVBoxLayout(self)

        # Title
        title_label = QLabel("STT Configuration Manager")
        title_label.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        main_layout.addWidget(title_label)

        # Splitter for list and editor
        splitter = QSplitter()

        # Left side - config list and buttons
        left_widget = self._create_left_panel()
        splitter.addWidget(left_widget)

        # Right side - config editor
        splitter.addWidget(self.config_editor)

        splitter.setSizes([200, 600])
        main_layout.addWidget(splitter)

        # Bottom buttons
        bottom_layout = QHBoxLayout()
        bottom_layout.addStretch()
        bottom_layout.addWidget(self.use_button)
        bottom_layout.addWidget(self.close_button)
        main_layout.addLayout(bottom_layout)

    def _create_left_panel(self):
        """Create the left panel with config list and buttons."""
        from PyQt6.QtWidgets import QWidget

        widget = QWidget()
        layout = QVBoxLayout(widget)

        # Config list label
        list_label = QLabel("Configurations:")
        list_label.setFont(QFont("Arial", 10, QFont.Weight.Bold))
        layout.addWidget(list_label)

        # Config list
        layout.addWidget(self.config_list)

        # Buttons
        buttons_layout = QVBoxLayout()

        buttons_layout.addWidget(self.new_button)
        buttons_layout.addWidget(self.duplicate_button)
        buttons_layout.addWidget(self.delete_button)

        buttons_layout.addStretch()
        layout.addLayout(buttons_layout)

        return widget

    def _populate_config_list(self):
        """Populate the configuration list."""
        self.config_list.clear()

        config_names = self.config_manager.get_config_names()
        for name in config_names:
            item = QListWidgetItem(name)
            self.config_list.addItem(item)

        # Select current config
        current_name = self.config_manager.get_current_config_name()
        if current_name:
            items = self.config_list.findItems(current_name, 0)
            if items:
                self.config_list.setCurrentItem(items[0])

    def _on_config_selected(self, current, previous):
        """Handle configuration selection in list."""
        if current:
            config_name = current.text()
            self.current_config_name = config_name

            config = self.config_manager.get_config(config_name)
            if config:
                self.config_editor.set_config(config)
                self.use_button.setEnabled(True)
                logger.debug(f"📋 Selected config: {config_name}")
            else:
                self.use_button.setEnabled(False)
                logger.error(f"❌ Config not found: {config_name}")
        else:
            self.current_config_name = None
            self.use_button.setEnabled(False)

    def _on_config_changed(self, config: STTConfig):
        """Handle config changes in editor."""
        # Mark as modified (could add visual indicator)
        pass

    def _on_save_requested(self, config: STTConfig):
        """Handle save request from editor."""
        try:
            # Validate config name
            if not config.name.strip():
                QMessageBox.warning(self, "Invalid Name", "Configuration name cannot be empty.")
                return

            # Check if name changed
            if self.current_config_name and config.name != self.current_config_name:
                # Name changed - create new config
                if config.name in self.config_manager.get_config_names():
                    QMessageBox.warning(self, "Name Exists", f"Configuration '{config.name}' already exists.")
                    return

                # Delete old config if it exists
                if self.current_config_name != "default-speech":
                    self.config_manager.delete_config(self.current_config_name)

            # Save config
            if self.config_manager.save_config(config):
                QMessageBox.information(self, "Success", f"Configuration '{config.name}' saved successfully.")
                self._populate_config_list()

                # Select the saved config
                items = self.config_list.findItems(config.name, 0)
                if items:
                    self.config_list.setCurrentItem(items[0])

                logger.info(f"💾 Saved config: {config.name}")
            else:
                QMessageBox.critical(self, "Save Failed", "Failed to save configuration.")

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error saving configuration: {str(e)}")
            logger.error(f"❌ Error saving config: {e}")

    def _on_cancel_requested(self):
        """Handle cancel request from editor."""
        # Reload current config
        if self.current_config_name:
            config = self.config_manager.get_config(self.current_config_name)
            if config:
                self.config_editor.set_config(config)

    def _on_new_clicked(self):
        """Handle new config button."""
        try:
            name, ok = QInputDialog.getText(self, "New Configuration", "Enter configuration name:")

            if ok and name.strip():
                name = name.strip()

                if name in self.config_manager.get_config_names():
                    QMessageBox.warning(self, "Name Exists", f"Configuration '{name}' already exists.")
                    return

                # Create new config
                new_config = self.config_manager.create_config(name)
                if new_config:
                    self._populate_config_list()

                    # Select new config
                    items = self.config_list.findItems(name, 0)
                    if items:
                        self.config_list.setCurrentItem(items[0])

                    logger.info(f"🆕 Created new config: {name}")
                else:
                    QMessageBox.critical(self, "Creation Failed", "Failed to create new configuration.")

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error creating configuration: {str(e)}")
            logger.error(f"❌ Error creating config: {e}")

    def _on_duplicate_clicked(self):
        """Handle duplicate config button."""
        if not self.current_config_name:
            QMessageBox.warning(self, "No Selection", "Please select a configuration to duplicate.")
            return

        try:
            name, ok = QInputDialog.getText(self, "Duplicate Configuration",
                                          f"Enter name for duplicate of '{self.current_config_name}':")

            if ok and name.strip():
                name = name.strip()

                if name in self.config_manager.get_config_names():
                    QMessageBox.warning(self, "Name Exists", f"Configuration '{name}' already exists.")
                    return

                # Duplicate config
                new_config = self.config_manager.duplicate_config(self.current_config_name, name)
                if new_config:
                    self._populate_config_list()

                    # Select new config
                    items = self.config_list.findItems(name, 0)
                    if items:
                        self.config_list.setCurrentItem(items[0])

                    logger.info(f"📋 Duplicated config: {self.current_config_name} -> {name}")
                else:
                    QMessageBox.critical(self, "Duplication Failed", "Failed to duplicate configuration.")

        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error duplicating configuration: {str(e)}")
            logger.error(f"❌ Error duplicating config: {e}")

    def _on_delete_clicked(self):
        """Handle delete config button."""
        if not self.current_config_name:
            QMessageBox.warning(self, "No Selection", "Please select a configuration to delete.")
            return

        if self.current_config_name == "default-speech":
            QMessageBox.warning(self, "Cannot Delete", "Cannot delete the default configuration.")
            return

        reply = QMessageBox.question(self, "Confirm Delete",
                                   f"Are you sure you want to delete configuration '{self.current_config_name}'?",
                                   QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)

        if reply == QMessageBox.StandardButton.Yes:
            try:
                if self.config_manager.delete_config(self.current_config_name):
                    QMessageBox.information(self, "Deleted", f"Configuration '{self.current_config_name}' deleted.")
                    self._populate_config_list()

                    # Clear selection
                    self.current_config_name = None
                    self.use_button.setEnabled(False)

                    logger.info(f"🗑️  Deleted config: {self.current_config_name}")
                else:
                    QMessageBox.critical(self, "Delete Failed", "Failed to delete configuration.")

            except Exception as e:
                QMessageBox.critical(self, "Error", f"Error deleting configuration: {str(e)}")
                logger.error(f"❌ Error deleting config: {e}")

    def _on_use_clicked(self):
        """Handle use config button."""
        if self.current_config_name:
            self.config_selected.emit(self.current_config_name)
            logger.info(f"✅ Selected config for use: {self.current_config_name}")
            self.accept()

    def _on_close_clicked(self):
        """Handle close button."""
        self.reject()

    def get_selected_config_name(self) -> str:
        """Get the name of the currently selected configuration."""
        return self.current_config_name or ""
