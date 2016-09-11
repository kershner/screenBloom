from time import sleep
import sb_controller
import ConfigParser
import webbrowser
import threading
import utility
import os


# Class for the start-up process
class StartupThread(threading.Thread):
    def __init__(self, host):
        super(StartupThread, self).__init__()
        self.stoprequest = threading.Event()
        self.host = host
        self.config_path = utility.get_config_path()

    def run(self):
        config_filename = '\\screenbloom_config.cfg'
        url = 'http://%s:5000/' % self.host
        if not self.stoprequest.isSet():
            # Check if config file has been created yet
            config_exists = os.path.isfile(self.config_path + config_filename)
            if config_exists:
                print 'Config already exists'
                config = ConfigParser.RawConfigParser()
                config.read(self.config_path + config_filename)
                utility.write_config('App State', 'running', '0')

                # Wait for 200 status code from server then load up interface
                while not utility.check_server(self.host):
                    sleep(0.2)

                sb_controller.init()
            else:
                # Config file doesn't exist, open New User interface
                print 'Config does not exist yet!'
                url += 'new-user'

        webbrowser.open(url)

    def join(self, timeout=None):
        self.stoprequest.set()
        super(StartupThread, self).join(timeout)
