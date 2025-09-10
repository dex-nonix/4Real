from nonix_web.plugin.base_plugin import add_configure_callback
from nonix_di import di_resolve
from .manager import NxDaemonManager


def daemons(classes):
    def _add_daemon(plugin, server, config):
        dm: NxDaemonManager = di_resolve(NxDaemonManager)
        for service_class in classes:
            dm.add_daemon(service_class)

    return lambda cls: add_configure_callback(cls, _add_daemon)
