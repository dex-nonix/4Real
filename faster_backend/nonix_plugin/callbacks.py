from functools import partial
from typing import Type, Callable

from .base import BasePlugin


def _add_callback(cls, attr_name, callback, args, kwargs):
    callbacks = getattr(cls, attr_name, None)
    if callbacks is None:
        callbacks = []
        setattr(cls, attr_name, callbacks)
    callbacks.append(partial(callback, *(args or []), **(kwargs or {})))
    return cls


def add_configure_callback(plugin_class: Type[BasePlugin], callback: Callable, args=None, kwargs=None):
    return _add_callback(plugin_class, "_configure_callbacks", callback, args, kwargs)


def add_startup_callback(plugin_class: Type[BasePlugin], callback: Callable, args=None, kwargs=None):
    return _add_callback(plugin_class, "_startup_callbacks", callback, args, kwargs)


def add_shutdown_callback(plugin_class: Type[BasePlugin], callback: Callable, args=None, kwargs=None):
    return _add_callback(plugin_class, "_shutdown_callbacks", callback, args, kwargs)
