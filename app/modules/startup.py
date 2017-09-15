from tornado.httpserver import HTTPServer
from tornado.wsgi import WSGIContainer
from tornado.ioloop import IOLoop
from config import params
import sb_controller
import webbrowser
import view_logic
import threading
import utility
import presets
import socket
import json
import os


# Class for the start-up process
class StartupThread(threading.Thread):
    def __init__(self, host, port, args, app):
        super(StartupThread, self).__init__()
        self.stoprequest = threading.Event()
        self.host = host
        self.port = port
        self.args = args
        self.app = app
        self.new_user = False
        self.needs_update = False
        self.error = False
        self.base_url = 'http://%s:%d/' % (self.host, self.port)
        self.url = None

    def run(self):
        if not self.stoprequest.isSet():
            if params.BUILD == 'win':
                # Check if config needs to be moved
                utility.move_files_check()

                # Initialize system tray menu
                SysTrayMenu(self)

            self.startup_checks()
            self.start_server()

    def join(self, timeout=None):
        self.stoprequest.set()
        super(StartupThread, self).join(timeout)

    def startup_checks(self):
        # Check For DLL error
        if params.BUILD == 'win':
            if not utility.dll_check():
                self.url = self.base_url + 'dll-error'
                self.error = True
                return

        # Check if config file has been created yet
        if os.path.isfile(utility.get_config_path()):
            # Check to see if config needs to be updated
            if not utility.config_check():
                self.url = self.base_url + 'update-config'
                self.needs_update = True
                return
            else:
                presets.update_presets_if_necessary()
                config = utility.get_config_dict()
                lights_initial_state = json.dumps(utility.get_hue_initial_state(config['ip'], config['username']))

                # Init Screen object with some first-run defaults
                utility.write_config('App State', 'running', False)
                utility.write_config('Light Settings', 'default', lights_initial_state)
                sb_controller.init()

                self.url = self.base_url
                return
        else:
            # Config file doesn't exist, open New User interface
            self.url = self.base_url + 'new-user'
            self.new_user = True
            return

    def start_server(self):
        try:
            http_server = HTTPServer(WSGIContainer(self.app))
            http_server.listen(self.port)

            if not self.needs_update and not self.error and not self.new_user:
                # Autostart check
                if not self.args.silent:
                    webbrowser.open(self.url)
                else:
                    config = utility.get_config_dict()
                    auto_start = config['autostart']
                    if auto_start:
                        sb_controller.start()

            # New User / Error / Needs Update - skip autostart
            else:
                webbrowser.open(self.url)

            IOLoop.instance().start()

        # Handle port collision
        except socket.error:
            self.port += 1
            self.start_server()


# System Tray Menu
class SysTrayMenu(object):
    def __init__(self, startup_thread, interval=1):
        self.interval = interval
        self.startup_thread = startup_thread
        thread = threading.Thread(target=self.run, args=())
        thread.daemon = True
        thread.start()

    def run(self):
        from modules.vendor import sys_tray_icon as sys_tray

        while True:
            base_path = os.path.dirname(os.path.abspath(__file__))
            if params.ENV == 'dev':
                icon_path = os.path.dirname(base_path) + '\\static\\images\\'
            else:
                icon_path = os.path.dirname(os.path.dirname(base_path)) + '\\'
            icon = icon_path + 'icon.ico'

            def open_ui(sys_tray_icon):
                url = 'http://%s:%d/' % (self.startup_thread.host, self.startup_thread.port)
                webbrowser.open(url)

            def start_sb_thread(sys_tray_icon):
                view_logic.start_screenbloom()

            def stop_sb_thread(sys_tray_icon):
                view_logic.stop_screenbloom()

            # Small helper to make dynamic 'apply preset' functions
            def make_func(preset_number):
                def _function(sys_tray_icon):
                    presets.apply_preset(preset_number)
                return _function

            all_presets = utility.get_all_presets()
            presets_buffer = []
            for index in all_presets:
                preset = all_presets[index]
                new_tray_entry = [preset['preset_name'], None, make_func(preset['preset_number'])]
                presets_buffer.append(new_tray_entry)

            presets_buffer.sort(key=lambda x: x[0])
            presets_tuple = tuple(tuple(x) for x in presets_buffer)

            hover_text = 'ScreenBloom'
            menu_options = (('Home', None, open_ui),
                            ('Start ScreenBloom', None, start_sb_thread),
                            ('Stop ScreenBloom', None, stop_sb_thread),
                            ('Presets', None, presets_tuple))

            def bye(sys_tray_icon):
                os._exit(1)

            sys_tray.SysTrayIcon(icon, hover_text, menu_options, on_quit=bye, default_menu_index=0)
