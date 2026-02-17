# Launch the UI when running: python -m talki_app
from .aio_talki_async import main as _ui_main

def main():
    """Package entrypoint — forwards to the UI main function."""
    return _ui_main()

if __name__ == "__main__":
    main()
