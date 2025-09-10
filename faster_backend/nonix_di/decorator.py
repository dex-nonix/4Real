from nonix_plugin import add_configure_callback
from . import di_register


def injectables(classes):
    def _add_services(plugin, config):
        for service_class in classes:
            di_register(service_class)

    return lambda cls: add_configure_callback(cls, _add_services)
