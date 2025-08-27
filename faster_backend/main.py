from nonix_web.server import NxWebServer

# settings.DEBUG = True

if __name__ == "__main__":
    NxWebServer.run_gunicorn()
