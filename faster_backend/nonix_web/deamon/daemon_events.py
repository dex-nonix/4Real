from enum import Enum


class DaemonEvents(Enum):
    """
    Enumeration for daemon-related events.
    """
    BEFORE_START = "before_start"
    AFTER_START = "after_start"
    BEFORE_STOP = "before_stop"
    AFTER_STOP = "after_stop"
    ERROR = "error"
    DAEMON_ADDED = "daemon_added"
    DAEMON_REMOVED = "daemon_removed"
