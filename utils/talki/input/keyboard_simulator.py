"""
Keyboard input simulation for typing text directly into applications.
"""

import time
from pynput import keyboard
from talki.config.logging_config import logger
from talki.utils.constants import CHARACTER_DELAY


class KeyboardSimulator:
    """
    Handles keyboard simulation for typing text and sending key presses.
    """

    def __init__(self):
        """Initialize the keyboard simulator."""
        self.keyboard_controller = keyboard.Controller()
        logger.debug("⌨️  Keyboard simulator initialized")

    def type_text(self, text: str):
        """
        Type text directly into the focused input field.

        Args:
            text: Text to type
        """
        try:
            logger.debug(f"📝 Typing {len(text)} characters directly...")

            for char in text:
                if char == '\n':
                    # Handle newlines by pressing Enter
                    self.keyboard_controller.tap(keyboard.Key.enter)
                elif char == '\t':
                    # Handle tabs
                    self.keyboard_controller.tap(keyboard.Key.tab)
                else:
                    # Type regular characters
                    self.keyboard_controller.type(char)

                # Small delay between characters for reliability
                time.sleep(CHARACTER_DELAY)

            logger.info("✅ Text typing completed")

        except Exception as e:
            logger.error(f"❌ Error typing text directly: {e}")
            raise

    def send_enter(self):
        """Send an Enter keypress."""
        logger.debug("⏎ Sending Enter keypress")
        try:
            self.keyboard_controller.tap(keyboard.Key.enter)
        except Exception as e:
            logger.error(f"❌ Error sending Enter keypress: {e}")
            raise

    def send_ctrl_enter(self):
        """Send a Ctrl+Enter keypress combination."""
        logger.debug("⏎ Sending Ctrl+Enter keypress")
        try:
            self.keyboard_controller.press(keyboard.Key.ctrl)
            self.keyboard_controller.tap(keyboard.Key.enter)
            self.keyboard_controller.release(keyboard.Key.ctrl)
        except Exception as e:
            logger.error(f"❌ Error sending Ctrl+Enter keypress: {e}")
            raise

    def send_key_combination(self, modifier_key: keyboard.Key, target_key: keyboard.Key):
        """
        Send a key combination with a modifier.

        Args:
            modifier_key: The modifier key (e.g., keyboard.Key.ctrl)
            target_key: The target key to press with modifier
        """
        try:
            self.keyboard_controller.press(modifier_key)
            self.keyboard_controller.tap(target_key)
            self.keyboard_controller.release(modifier_key)
        except Exception as e:
            logger.error(f"❌ Error sending key combination: {e}")
            raise
