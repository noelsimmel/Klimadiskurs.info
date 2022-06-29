# Run file
# Creates an app instance and runs it
# You can start a local instance with python run.py
# Activate the virtual environment first: https://docs.python.org/3/tutorial/venv.html

from klimadiskurs import create_app
from klimadiskurs.config import Config

app = create_app()
app.logger.debug("App creation finished")

if __name__ == "__main__":
    app.run(debug=Config.DEBUG_MODE)
