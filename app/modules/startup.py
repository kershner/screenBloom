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
import itertools
import utility
import presets
import socket
import glob
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
                # Check to see if config needs to be updated
                if not utility.config_check():
                    url = base_url + 'update-config'
                else:
                    presets.update_presets_if_necessary()

                    # Init Screen object
                    utility.write_config('Configuration', 'color_mode_enabled', False)
                    sb_controller.init()
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


class SysTrayMenu(object):
    def __init__(self, interval=1):
        self.interval = interval
        thread = threading.Thread(target=self.run, args=())
        thread.daemon = True
        thread.start()

    def run(self):
        while True:
            print 'POOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOPSOCK'
            from modules.vendor import sys_tray_icon as sys_tray

            icon_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__))) + '\\static\\images\\'
            icons = itertools.cycle(glob.glob(icon_path + '*.ico'))

            def hello(sysTrayIcon): print "Hello World."

            def simon(sysTrayIcon): print "Hello Simon."

            def switch_icon(sys_tray_icon):
                print 'You need other icons for this to work dipshit'
                sys_tray_icon.icon = icons.next()
                sys_tray_icon.refresh_icon()

            hover_text = 'ScreenBloom'
            menu_options = (('Say Hello', None, hello),
                            ('Switch Icon', None, switch_icon),
                            ('A sub-menu', None, (('Say Hello to Simon', None, simon),
                                                  ('Switch Icon', None, switch_icon),
                                                  ))
                            )

            def bye(sys_tray_icon):
                print 'Bye!'
                os._exit(1)

            sys_tray.SysTrayIcon(icons.next(), hover_text, menu_options, on_quit=bye, default_menu_index=1)


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
