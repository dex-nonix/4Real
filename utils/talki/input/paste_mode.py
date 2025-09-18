"""
Paste mode functionality with mouse and keyboard listeners.
"""

from typing import Callable, Optional
from pynput import keyboard, mouse
from PyQt6.QtCore import QTimer
from talki.config.logging_config import logger
from talki.input.keyboard_simulator import KeyboardSimulator
from talki.utils.constants import PASTE_LISTENER_DELAY


class PasteMode:
    """
    Manages paste mode functionality with mouse and keyboard listeners.

    Paste mode allows users to click to focus windows and Ctrl+Click to paste text.
    """

    def __init__(self, keyboard_simulator: KeyboardSimulator):
        """
        Initialize paste mode.

        Args:
            keyboard_simulator: KeyboardSimulator instance for text input
        """
        self.keyboard_simulator = keyboard_simulator

        # State
        self.active = False
        self.pending_text = None
        self.ctrl_pressed = False

        # Listeners
        self.mouse_listener = None
        self.keyboard_listener = None

        # Callbacks
        self.on_paste_completed = None  # Called when paste operation completes
        self.on_mode_cancelled = None   # Called when mode is cancelled

        logger.debug("🎯 Paste mode initialized")

    def start_paste_mode(self, text: str, on_completed: Optional[Callable] = None,
                        on_cancelled: Optional[Callable] = None):
        """
        Start paste mode with the specified text.

        Args:
            text: Text to paste when Ctrl+Click is detected
            on_completed: Callback when paste completes successfully
            on_cancelled: Callback when mode is cancelled
        """
        if self.active:
            logger.warning("⚠️  Paste mode already active")
            return

        self.pending_text = text
        self.on_paste_completed = on_completed
        self.on_mode_cancelled = on_cancelled

        self.active = True
        logger.info("🎯 Paste mode enabled - regular clicks focus windows, Ctrl+Click pastes")

        # Small delay to let focus settle before enabling listeners
        QTimer.singleShot(PASTE_LISTENER_DELAY, self._enable_listeners)

    def stop_paste_mode(self):
        """Stop paste mode and clean up listeners."""
        if not self.active:
            logger.debug("🔇 Paste mode not active, ignoring stop request")
            return

        logger.info("🛑 Disabling paste mode listeners...")
        self.active = False
        self.pending_text = None

        # Stop listeners
        self._stop_mouse_listener()
        self._stop_keyboard_listener()

        # Call cancellation callback if set
        if self.on_mode_cancelled:
            try:
                self.on_mode_cancelled()
            except Exception as e:
                logger.error(f"❌ Error in mode cancelled callback: {e}")

        logger.info("✅ Paste mode disabled")

    def is_active(self) -> bool:
        """Check if paste mode is currently active."""
        return self.active

    def _enable_listeners(self):
        """Enable mouse and keyboard listeners for paste mode."""
        try:
            logger.debug("🐭 Starting paste mode mouse listener...")
            self.mouse_listener = mouse.Listener(on_click=self._on_mouse_click)
            self.mouse_listener.start()

            logger.debug("⌨️  Starting paste mode keyboard listener...")
            self.keyboard_listener = keyboard.Listener(
                on_press=self._on_key_press,
                on_release=self._on_key_release
            )
            self.keyboard_listener.start()

            logger.info("✅ Paste mode active - Regular clicks focus, Ctrl+Click ONLY pastes, ESC cancels")
            logger.debug(f"🔍 Initial ctrl_pressed state: {self.ctrl_pressed}")

        except Exception as e:
            logger.error(f"❌ Failed to enable paste listeners: {e}")
            self.stop_paste_mode()

    def _stop_mouse_listener(self):
        """Stop the mouse listener."""
        if self.mouse_listener:
            try:
                self.mouse_listener.stop()
            except Exception as e:
                logger.error(f"❌ Error stopping mouse listener: {e}")
            self.mouse_listener = None

    def _stop_keyboard_listener(self):
        """Stop the keyboard listener."""
        if self.keyboard_listener:
            try:
                self.keyboard_listener.stop()
            except Exception as e:
                logger.error(f"❌ Error stopping keyboard listener: {e}")
            self.keyboard_listener = None

    def _on_mouse_click(self, x, y, button, pressed):
        """
        Handle mouse click events in paste mode.

        Args:
            x, y: Mouse coordinates
            button: Mouse button pressed
            pressed: True if button was pressed, False if released
        """
        if not pressed or not self.active or button != mouse.Button.left:
            return

        logger.debug(f"🖱️  Click detected at ({x}, {y}) - ctrl_pressed = {self.ctrl_pressed}")

        if self.ctrl_pressed:
            # Ctrl+Click triggers paste
            logger.info(f"🎯 Ctrl+Click detected at ({x}, {y}) - capturing text and pasting")
            self._execute_paste()
        else:
            # Regular click - just focus the window
            logger.debug(f"🖱️  Regular click at ({x}, {y}) - focusing window/area only (NO PASTE)")

    def _on_key_press(self, key):
        """
        Handle key press events in paste mode.

        Args:
            key: Key that was pressed
        """
        try:
            if key == keyboard.Key.esc and self.active:
                logger.info("🚫 Paste mode: Escape key pressed - canceling")
                self.stop_paste_mode()
                return False  # Stop the listener
            elif key in (keyboard.Key.ctrl_l, keyboard.Key.ctrl_r):
                logger.debug("🔑 Paste mode: Ctrl key pressed - setting ctrl_pressed = True")
                self.ctrl_pressed = True
                logger.debug(f"🔍 Ctrl state: {self.ctrl_pressed}")
        except Exception as e:
            logger.error(f"❌ Error in key press handler: {e}")

    def _on_key_release(self, key):
        """
        Handle key release events in paste mode.

        Args:
            key: Key that was released
        """
        try:
            if key in (keyboard.Key.ctrl_l, keyboard.Key.ctrl_r):
                logger.debug("🔓 Paste mode: Ctrl key released - setting ctrl_pressed = False")
                self.ctrl_pressed = False
                logger.debug(f"🔍 Ctrl state: {self.ctrl_pressed}")
        except Exception as e:
            logger.error(f"❌ Error in key release handler: {e}")

    def _execute_paste(self):
        """Execute the paste operation."""
        if not self.pending_text:
            logger.warning("⚠️  No text available to paste")
            self.stop_paste_mode()
            return

        logger.info("⌨️  Executing paste operation...")

        try:
            # Type the text directly
            self.keyboard_simulator.type_text(self.pending_text)
            logger.info("✅ Paste operation completed")

            # Call completion callback if set
            if self.on_paste_completed:
                try:
                    self.on_paste_completed()
                except Exception as e:
                    logger.error(f"❌ Error in paste completed callback: {e}")

        except Exception as e:
            logger.error(f"❌ Error executing paste: {e}")

        # Stop paste mode after paste operation
        self.stop_paste_mode()
