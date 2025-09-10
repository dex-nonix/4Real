from enum import Enum


class NxDaemonEvents(Enum):
    """
    Enumeration for daemon-related events.
    """
    BEFORE_START = "before_start"
    AFTER_START = "after_start"
    BEFORE_STOP = "before_stop"
    AFTER_STOP = "after_stop"
    ERROR = "error"


class NxDaemonManagerEvents(Enum):
    """
    Enumeration for daemon manager-related events.
    """
    DAEMON_ADDED = "daemon_added"
    DAEMON_REMOVED = "daemon_removed"
    BEFORE_START_ALL = "before_start_all"
    AFTER_START_ALL = "after_start_all"
    BEFORE_STOP_ALL = "before_stop_all"
    AFTER_STOP_ALL = "after_stop_all"
    MANAGER_ERROR = "manager_error"
