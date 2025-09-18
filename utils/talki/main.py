"""
Main entry point for the Talki application.
"""

import sys
from PyQt6.QtWidgets import QApplication
from talki.config.logging_config import logger
from talki.ui.main_window import MainWindow
from talki.services.application_service import ApplicationService
from talki.utils.constants import FEATURES


def main():
    """Main application entry point."""
    logger.info("🚀 Starting Talki Real-Time Transcription Application")
    logger.info("=" * 60)

    try:
        logger.debug("📱 Creating QApplication...")
        app = QApplication(sys.argv)

        logger.debug("🏠 Creating MainWindow...")
        window = MainWindow()

        logger.debug("🎯 Creating Application Service...")
        app_service = ApplicationService()
        app_service.initialize_components(window)

        logger.debug("🖥️  Showing main window...")
        window.show()

        logger.info("✅ Application initialized and ready")
        logger.info("🎤 Features available:")

        for feature in FEATURES:
            logger.info(f"   • {feature}")

        logger.info("=" * 60)

        # Start the Qt event loop
        sys.exit(app.exec())

    except Exception as e:
        logger.error(f"❌ Fatal error during application startup: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
