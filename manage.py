from kombu import Queue
from crochet import run_in_reactor
from flask_script import Manager, Server
from flask_migrate import Migrate, MigrateCommand
from app import app, db, wapp


migrate = Migrate(app, db)
manager = Manager(app)
server = Server(
    host=app.config['HOST'], 
    port=app.config['PORT']
)
manager.add_command('db', MigrateCommand)
manager.add_command('runserver', server)

if __name__ == '__main__':
    import sys
    import logging

    logging.basicConfig(
        stream=sys.stderr, 
        level=logging.DEBUG
    )
    @run_in_reactor
    def start_wamp():
        wapp.run(
            u"ws://localhost:8080/ws", 
            u"realm1", 
            start_reactor=False
        )

    start_wamp()
    manager.run()
