from config import params
from time import sleep
from copy import copy
import sb_controller
import ConfigParser
import webbrowser
import threading
import utility
import presets
import os


# Class for the start-up process
class StartupThread(threading.Thread):
    def __init__(self, host):
        super(StartupThread, self).__init__()
        self.stoprequest = threading.Event()
        self.host = host

    def run(self):
        base_url = 'http://%s:5000/' % self.host
        url = copy(base_url)
        print 'Welcome to ScreenBloom!'
        print 'Server running at: %s' % base_url
        if not self.stoprequest.isSet():
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
                    config = ConfigParser.RawConfigParser()
                    config.read(utility.get_config_path())
                    utility.write_config('App State', 'running', '0')
                    sb_controller.start()
            else:
                # Config file doesn't exist, open New User interface
                print 'Redirecting to New User interface...'
                url = base_url + 'new-user'

        # Wait for 200 status code from server then load up interface
        while not utility.check_server(self.host):
            sleep(0.2)
        webbrowser.open(url)

    def join(self, timeout=None):
        self.stoprequest.set()
        super(StartupThread, self).join(timeout)
