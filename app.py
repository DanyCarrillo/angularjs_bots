import os
from app import app
from flask_script import Server, Manager

app.config.from_pyfile('../config.py')
server = Server(host=app.config['HOST'], port=app.config['PORT'])
manager = Manager(app)
manager.add_command('runserver', server)
if __name__ == '__main__':
    import sys
    import logging

    logging.basicConfig(stream=sys.stderr, level=logging.DEBUG)

    app.run(host=app.config['HOST'], port=app.config['PORT'])
