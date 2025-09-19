"""
Generic STTConfigEditor component - Reusable config editor for all STT configurations.
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QComboBox,
    QCheckBox, QSpinBox, QDoubleSpinBox, QGroupBox, QScrollArea,
    QTextEdit, QPushButton, QFormLayout, QTabWidget, QSplitter
)
from PyQt6.QtCore import pyqtSignal
from PyQt6.QtGui import QFont
from talki.config.logging_config import logger
from talki.core.stt_engine import STTConfig


class STTConfigEditor(QWidget):
    """
    Generic STT configuration editor component.
    Can be used in dialogs, sidepanes, or anywhere config editing is needed.
    """

    # Signals
    config_changed = pyqtSignal(STTConfig)  # Emitted when config is modified
    save_requested = pyqtSignal(STTConfig)  # Emitted when save is requested
    cancel_requested = pyqtSignal()         # Emitted when cancel is requested

    def __init__(self, config: STTConfig = None, parent=None):
        """Initialize config editor."""
        super().__init__(parent)

        self.original_config = config or STTConfig()
        self.current_config = STTConfig.from_dict(self.original_config.to_dict())

        # UI Elements
        self.name_edit = None
        self.version_edit = None
        self.enabled_check = None

        # Engine preset widgets
        self.engine_type_combo = None
        self.model_combo = None
        self.device_combo = None
        self.compute_type_combo = None

        # Preprocess preset widgets
        self.resample_spin = None
        self.vad_enabled_check = None
        self.denoise_enabled_check = None
        self.normalize_enabled_check = None

        # Streaming preset widgets
        self.frame_ms_spin = None
        self.partial_results_check = None
        self.endpointing_enabled_check = None
        self.max_session_minutes_spin = None

        # Feature preset widgets
        self.language_detection_check = None
        self.timestamps_check = None
        self.punctuation_check = None

        # Postprocess preset widgets
        self.remove_fillers_check = None
        self.capitalize_sentences_check = None

        self._create_ui()
        self._setup_layout()
        self._populate_values()

        logger.debug("📝 STTConfigEditor initialized")

    def _create_ui(self):
        """Create all UI elements."""
        # Basic config
        self.name_edit = QLineEdit()
        self.version_edit = QLineEdit()
        self.enabled_check = QCheckBox("Enabled")

        # Engine preset
        self.engine_type_combo = QComboBox()
        self.engine_type_combo.addItems(["whisper", "vosk"])
        self.model_combo = QComboBox()
        self.model_combo.addItems(["tiny", "tiny.en", "base", "base.en", "small", "small.en", "medium", "medium.en", "large-v1", "large-v2", "large-v3"])
        self.device_combo = QComboBox()
        self.device_combo.addItems(["cpu", "cuda"])
        self.compute_type_combo = QComboBox()
        self.compute_type_combo.addItems(["int8", "float16", "float32"])

        # Preprocess preset
        self.resample_spin = QSpinBox()
        self.resample_spin.setRange(8000, 48000)
        self.resample_spin.setValue(16000)
        self.vad_enabled_check = QCheckBox("Voice Activity Detection")
        self.denoise_enabled_check = QCheckBox("Denoising")
        self.normalize_enabled_check = QCheckBox("Normalization")

        # Streaming preset
        self.frame_ms_spin = QSpinBox()
        self.frame_ms_spin.setRange(10, 1000)
        self.frame_ms_spin.setValue(100)
        self.partial_results_check = QCheckBox("Partial Results")
        self.endpointing_enabled_check = QCheckBox("Endpointing")
        self.max_session_minutes_spin = QSpinBox()
        self.max_session_minutes_spin.setRange(1, 1440)  # 1 minute to 24 hours
        self.max_session_minutes_spin.setValue(60)

        # Feature preset
        self.language_detection_check = QCheckBox("Language Detection")
        self.timestamps_check = QCheckBox("Timestamps")
        self.punctuation_check = QCheckBox("Punctuation")

        # Postprocess preset
        self.remove_fillers_check = QCheckBox("Remove Fillers")
        self.capitalize_sentences_check = QCheckBox("Capitalize Sentences")

        # Connect signals
        self._connect_signals()

    def _connect_signals(self):
        """Connect all UI signals to handlers."""
        # Basic config
        self.name_edit.textChanged.connect(self._on_config_changed)
        self.version_edit.textChanged.connect(self._on_config_changed)
        self.enabled_check.toggled.connect(self._on_config_changed)

        # Engine preset
        self.engine_type_combo.currentTextChanged.connect(self._on_config_changed)
        self.model_combo.currentTextChanged.connect(self._on_config_changed)
        self.device_combo.currentTextChanged.connect(self._on_config_changed)
        self.compute_type_combo.currentTextChanged.connect(self._on_config_changed)

        # Preprocess preset
        self.resample_spin.valueChanged.connect(self._on_config_changed)
        self.vad_enabled_check.toggled.connect(self._on_config_changed)
        self.denoise_enabled_check.toggled.connect(self._on_config_changed)
        self.normalize_enabled_check.toggled.connect(self._on_config_changed)

        # Streaming preset
        self.frame_ms_spin.valueChanged.connect(self._on_config_changed)
        self.partial_results_check.toggled.connect(self._on_config_changed)
        self.endpointing_enabled_check.toggled.connect(self._on_config_changed)
        self.max_session_minutes_spin.valueChanged.connect(self._on_config_changed)

        # Feature preset
        self.language_detection_check.toggled.connect(self._on_config_changed)
        self.timestamps_check.toggled.connect(self._on_config_changed)
        self.punctuation_check.toggled.connect(self._on_config_changed)

        # Postprocess preset
        self.remove_fillers_check.toggled.connect(self._on_config_changed)
        self.capitalize_sentences_check.toggled.connect(self._on_config_changed)

    def _setup_layout(self):
        """Set up the component layout with tabs."""
        main_layout = QVBoxLayout(self)

        # Tab widget for different preset categories
        self.tab_widget = QTabWidget()

        # Basic config tab
        basic_tab = self._create_basic_tab()
        self.tab_widget.addTab(basic_tab, "Basic")

        # Engine tab
        engine_tab = self._create_engine_tab()
        self.tab_widget.addTab(engine_tab, "Engine")

        # Preprocess tab
        preprocess_tab = self._create_preprocess_tab()
        self.tab_widget.addTab(preprocess_tab, "Preprocess")

        # Streaming tab
        streaming_tab = self._create_streaming_tab()
        self.tab_widget.addTab(streaming_tab, "Streaming")

        # Features tab
        features_tab = self._create_features_tab()
        self.tab_widget.addTab(features_tab, "Features")

        # Postprocess tab
        postprocess_tab = self._create_postprocess_tab()
        self.tab_widget.addTab(postprocess_tab, "Postprocess")

        main_layout.addWidget(self.tab_widget)

        # Action buttons
        buttons_layout = QHBoxLayout()
        save_button = QPushButton("💾 Save")
        save_button.clicked.connect(self._on_save_clicked)
        cancel_button = QPushButton("❌ Cancel")
        cancel_button.clicked.connect(self._on_cancel_clicked)

        buttons_layout.addStretch()
        buttons_layout.addWidget(save_button)
        buttons_layout.addWidget(cancel_button)
        main_layout.addLayout(buttons_layout)

    def _create_basic_tab(self):
        """Create basic configuration tab."""
        widget = QWidget()
        layout = QFormLayout(widget)

        layout.addRow("Name:", self.name_edit)
        layout.addRow("Version:", self.version_edit)
        layout.addRow("", self.enabled_check)

        return widget

    def _create_engine_tab(self):
        """Create engine configuration tab."""
        widget = QWidget()
        layout = QFormLayout(widget)

        layout.addRow("Engine Type:", self.engine_type_combo)
        layout.addRow("Model:", self.model_combo)
        layout.addRow("Device:", self.device_combo)
        layout.addRow("Compute Type:", self.compute_type_combo)

        return widget

    def _create_preprocess_tab(self):
        """Create preprocessing configuration tab."""
        widget = QWidget()
        layout = QFormLayout(widget)

        layout.addRow("Sample Rate (Hz):", self.resample_spin)
        layout.addRow("", self.vad_enabled_check)
        layout.addRow("", self.denoise_enabled_check)
        layout.addRow("", self.normalize_enabled_check)

        return widget

    def _create_streaming_tab(self):
        """Create streaming configuration tab."""
        widget = QWidget()
        layout = QFormLayout(widget)

        layout.addRow("Frame Size (ms):", self.frame_ms_spin)
        layout.addRow("", self.partial_results_check)
        layout.addRow("", self.endpointing_enabled_check)
        layout.addRow("Max Session (min):", self.max_session_minutes_spin)

        return widget

    def _create_features_tab(self):
        """Create features configuration tab."""
        widget = QWidget()
        layout = QFormLayout(widget)

        layout.addRow("", self.language_detection_check)
        layout.addRow("", self.timestamps_check)
        layout.addRow("", self.punctuation_check)

        return widget

    def _create_postprocess_tab(self):
        """Create postprocessing configuration tab."""
        widget = QWidget()
        layout = QFormLayout(widget)

        layout.addRow("", self.remove_fillers_check)
        layout.addRow("", self.capitalize_sentences_check)

        return widget

    def _populate_values(self):
        """Populate UI with current config values."""
        config = self.current_config

        # Basic config
        self.name_edit.setText(config.name)
        self.version_edit.setText(config.version)
        self.enabled_check.setChecked(config.enabled)

        # Engine preset
        engine_preset = config.engine_preset
        self.engine_type_combo.setCurrentText(engine_preset.type)
        self.model_combo.setCurrentText(engine_preset.model)
        self.device_combo.setCurrentText(engine_preset.device)
        self.compute_type_combo.setCurrentText(engine_preset.compute_json.get("compute_type", "int8"))

        # Preprocess preset
        preprocess_preset = config.preprocess_preset
        self.resample_spin.setValue(preprocess_preset.resample_hz)
        self.vad_enabled_check.setChecked(preprocess_preset.vad_json.get("enabled", False))
        self.denoise_enabled_check.setChecked(preprocess_preset.denoise_json.get("enabled", False))
        self.normalize_enabled_check.setChecked(preprocess_preset.normalize_json.get("enabled", True))

        # Streaming preset
        streaming_preset = config.streaming_preset
        self.frame_ms_spin.setValue(streaming_preset.frame_ms)
        self.partial_results_check.setChecked(streaming_preset.partial_results)
        self.endpointing_enabled_check.setChecked(streaming_preset.endpointing_json.get("enabled", False))
        self.max_session_minutes_spin.setValue(streaming_preset.max_session_minutes)

        # Feature preset
        feature_preset = config.feature_preset
        self.language_detection_check.setChecked(feature_preset.language_detection)
        self.timestamps_check.setChecked(feature_preset.timestamps)
        self.punctuation_check.setChecked(feature_preset.punctuation)

        # Postprocess preset
        postprocess_preset = config.postprocess_preset
        self.remove_fillers_check.setChecked(postprocess_preset.remove_fillers)
        self.capitalize_sentences_check.setChecked(postprocess_preset.capitalize_sentences)

    def _collect_values(self) -> STTConfig:
        """Collect values from UI into config object."""
        config = STTConfig()

        # Basic config
        config.name = self.name_edit.text()
        config.version = self.version_edit.text()
        config.enabled = self.enabled_check.isChecked()

        # Engine preset
        config.engine_preset.type = self.engine_type_combo.currentText()
        config.engine_preset.model = self.model_combo.currentText()
        config.engine_preset.device = self.device_combo.currentText()
        config.engine_preset.compute_json = {"compute_type": self.compute_type_combo.currentText()}

        # Preprocess preset
        config.preprocess_preset.resample_hz = self.resample_spin.value()
        config.preprocess_preset.vad_json["enabled"] = self.vad_enabled_check.isChecked()
        config.preprocess_preset.denoise_json["enabled"] = self.denoise_enabled_check.isChecked()
        config.preprocess_preset.normalize_json["enabled"] = self.normalize_enabled_check.isChecked()

        # Streaming preset
        config.streaming_preset.frame_ms = self.frame_ms_spin.value()
        config.streaming_preset.partial_results = self.partial_results_check.isChecked()
        config.streaming_preset.endpointing_json["enabled"] = self.endpointing_enabled_check.isChecked()
        config.streaming_preset.max_session_minutes = self.max_session_minutes_spin.value()

        # Feature preset
        config.feature_preset.language_detection = self.language_detection_check.isChecked()
        config.feature_preset.timestamps = self.timestamps_check.isChecked()
        config.feature_preset.punctuation = self.punctuation_check.isChecked()

        # Postprocess preset
        config.postprocess_preset.remove_fillers = self.remove_fillers_check.isChecked()
        config.postprocess_preset.capitalize_sentences = self.capitalize_sentences_check.isChecked()

        return config

    def _on_config_changed(self):
        """Handle any config value change."""
        self.current_config = self._collect_values()
        self.config_changed.emit(self.current_config)

    def _on_save_clicked(self):
        """Handle save button click."""
        self.current_config = self._collect_values()
        self.save_requested.emit(self.current_config)

    def _on_cancel_clicked(self):
        """Handle cancel button click."""
        self.cancel_requested.emit()

    def get_config(self) -> STTConfig:
        """Get current configuration."""
        return self.current_config

    def set_config(self, config: STTConfig):
        """Set configuration and update UI."""
        self.current_config = STTConfig.from_dict(config.to_dict())
        self._populate_values()

    def has_changes(self) -> bool:
        """Check if current config differs from original."""
        return self.current_config.to_dict() != self.original_config.to_dict()
