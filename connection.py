import threading
import socket
import queue
import time
from common import *


class ConnectionThread(threading.Thread):
    '''An abstraction of a connection, representing a single user.'''
    def __init__(self, ID, addr=None, conn=None):
        '''If conn exists then serves as a server, if not then a client.'''
        self.conn = conn
        self.addr = addr
        self.pool = queue.Queue()
        self.first_data = True
        
        super(ConnectionThread, self).__init__()

    def run(self):
        if not self.conn:  # if as a client
            self.conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.conn.connect(addr)
        else: pass  # if as a server

        while True:
            pool = self.pool
            event = pool.get() if not pool.empty() else None

            if not event:
                time.sleep(0.2)
            elif event['Action'] == 'Send':
                pass
            elif event['Action'] == 'Recv':
                data = self.conn.recv(1024)
                #  if not EOF: data = self.conn.recv(1024)
                pool.put(gen_dict(Action='NewData', Data=data, pool=self.pool,
                    addr=self.addr, first_data=self.first_data))
                self.first_data = False
            elif event['Action'] == 'Exit':
                pass