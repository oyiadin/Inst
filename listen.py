import connection
import threading
import socket
from config import *


class ListeningThread(threading.Thread):
    def __init__(self, mainPool, ID):
        self.mainPool = mainPool
        self.ID = ID
        super(ListeningThread, self).__init__()

    def run(self):
        self.conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.conn.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        addr = config['Connection']['Host'].split(':')
        self.conn.bind((addr[0], int(addr[1])))

        while True:
            self.conn.listen(1)

            conn, addr = self.conn.accept()
            connThread = connection.ConnectionThread(self.ID, addr, conn)
            connThread.pool.put({'Action': 'Recv'})
            connThread.start()
