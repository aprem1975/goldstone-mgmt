import sys
import os

from .base import Object, InvalidInput, Completer
from pyang import repository, context
from .library import tabular
import json
import libyang as ly
import sysrepo as sr
import base64
import struct

from prompt_toolkit.document import Document
from prompt_toolkit.completion import WordCompleter, Completion, NestedCompleter


class Interface(Object):
    XPATH = '/'

    def close(self):
        self.session.stop()

    def xpath(self):
        self.path = '/sonic-port:sonic-port/PORT/PORT_LIST'
        return "{}[ifname='{}']".format(self.path, self.ifname)

    def __init__(self, conn, parent, ifname):
        self.session = conn.start_session()
        self.ifname = ifname
        super(Interface, self).__init__(parent)
        self.no_dict = {
                         'shutdown': None
                       }
                           
        
        @self.command(NestedCompleter.from_nested_dict(self.no_dict))
        def no(args):
            if (len(args) < 1):
               raise InvalidInput('usage: no shutdown')
            self.set_param('admin_status', 'up')


        @self.command()
        def shutdown(args):
            if (len(args) != 0):
               raise InvalidInput('usage: shutdown')
            self.set_param('admin_status', 'down')
          


    def set_param(self, param, value):
        v = value
        self.session.switch_datastore('operational')
        try:
            self.session.set_item('{}/{}'.format(self.xpath(), param), v)
            self.session.apply_changes()
        except sr.errors.SysrepoCallbackFailedError as e:
            print(e)
        self.session.switch_datastore('running')

    def __str__(self):
        return 'interface({})'.format(self.ifname)

