from tornado.httpserver import HTTPServer
from tornado.wsgi import WSGIContainer
from tornado.ioloop import IOLoop
from config import params
from time import sleep
from copy import copy
import sb_controller
import webbrowser
import view_logic
import threading
import utility
import presets
import socket
import os


# Class for the start-up process
class StartupThread(threading.Thread):
    def __init__(self, host, port, args):
        super(StartupThread, self).__init__()
        self.stoprequest = threading.Event()
        self.host = host
        self.port = port
        self.args = args

    def run(self):
        base_url = 'http://%s:%d/' % (self.host, self.port)
        url = copy(base_url)
        print 'Welcome to ScreenBloom!'
        print 'Server running at: %s' % base_url

        if not self.stoprequest.isSet():
            # Startup checks
            if params.BUILD == 'win':
                # Check For DLL error
                if not utility.dll_check():
                    url = base_url + 'dll-error'
            # Check if config file has been created yet
            if os.path.isfile(utility.get_config_path()):
                presets.update_presets_if_necessary()
                # Check to see if config needs to be updated
                if not utility.config_check():
                    url = base_url + 'update-config'
                else:
                    utility.write_config('Configuration', 'color_mode_enabled', False)
                    sb_controller.start()
            else:
                # Config file doesn't exist, open New User interface
                print 'Redirecting to New User interface...'
                url = base_url + 'new-user'

        # Wait for 200 status code from server then load up interface
        while not utility.check_server(self.host, self.port):
            sleep(0.2)

        webbrowser.open(url)

    def join(self, timeout=None):
        self.stoprequest.set()
        super(StartupThread, self).join(timeout)


# Handles choosing a port and starting Tornado server
def start_server(app, startup_thread):
    try:
        http_server = HTTPServer(WSGIContainer(app))
        http_server.listen(startup_thread.port)

        if not startup_thread.args.silent:
            startup_thread.start()
        else:
            config = utility.get_config_dict()
            auto_start = config['autostart']

            sb_controller.start()
            if auto_start:
                view_logic.start_screenbloom()

        IOLoop.instance().start()

    # Handle port collision
    except socket.error:
        startup_thread.port += 1
        start_server(app, startup_thread)
