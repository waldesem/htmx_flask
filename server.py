from app import create_app
from webgui import FlaskUI


def main():
    app = create_app()
    FlaskUI(server_kwargs={"app": app, "host": "127.0.0.1", "port": 5000}).run()


if __name__ == "__main__":
    main()
