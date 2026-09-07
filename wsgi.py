"""Entry point used by production WSGI servers (gunicorn, PythonAnywhere, etc.)."""

from app import create_app

app = create_app("production")

if __name__ == "__main__":
    app.run()
