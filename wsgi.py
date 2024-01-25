"""
The WSGI entry point for our application.

The WSGI server will call this file to serve the app.

https://flask.palletsprojects.com/en/3.0.x/deploying/
"""

from app import create_app

app = create_app()

if __name__ == "__main__":

    app.run()
