import threading
import queue
import configparser
import socket
import string
import random


class EventPool(queue.Queue):
    '''This class implements a simple event-pool module.'''
    def __init__(self, name=''.join(random.sample(string.hexdigits, 4)),
        actNoEvent=lambda:None):

        self.name = name
        self.actNoEvent = actNoEvent
        super(EventPool, self).__init__()

    def popEvent(self):
        if not self.empty():
            return self.get()
        else:
            self.actNoEvent()

    def putEvent(self, handler, **argvs):
        self.put({'Handler': handler, **argvs})


class Connection(threading.Thread, socket.socket):
    '''This class supplies some common operations for some other sub-classes.

    Each instance of this class represents a connection with a specific host.
    And each instance will run as a separate thread, using two queue objects to
    communicate the main thread.
    '''
    def __init__(self, host, port, hisEventPool, recvHandler):
        '''
        @host: hostname as a string
        @port: both string and int are okay
        @eventPool: an instance of queue.Queue, be used to communicate
        @recvHandler: a function object, will be called when data comes
        '''
        self.connName = 'Conn-' + ''.join(random.sample(string.hexdigits, 4))
        self.recvHandler = recvHandler
        self.addr = (host, int(port))
        self.hisEventPool = hisEventPool
        self.ownEventPool = EventPool(self.connName, self.actNoEvent)

        super(Connection, self).__init__(name=self.connName)
        socket.socket.__init__(self, socket.AF_INET, socket.SOCK_STREAM)
        self.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    def bind(self):
        super(Connection, self).bind(self.addr)

    def connect(self):
        super(Connection, self).connect(self.addr)

    def mainLoop(self):
        '''Deal with each event in the ownEventPool.(FIFO)

        A dict is the representation of an event.
        '''
        while True:
            event = self.ownEventPool.popEvent()
            if event['Action'] == 'Send':
                self.conn.sendall(event['Data'])
            elif event['Action'] == 'Recv':
                self.hisEventPool.put({
                    'Handler':      self.recvHandler,
                    'Data':         self.recv(),
                    'Connection':   self.conn,
                    'EventPool':    self.ownEventPool})
            elif event['Action'] == 'Exit':
                self.close()
                break

    def actNoEvent(self): print('No Event!')


class Connection_Server(Connection):
    def start(self):
        self.bind()
        self.listen(1)
        super(Connection_Server, self).start()
        self.conn = self.accept()[0]
        self.mainLoop()

    def actNoEvent(self):
        '''To enter the recv-mode when no more events in pool.'''
        self.ownEventPool.put({'Action': 'Recv'})


class Connection_Client(Connection):
    def start(self):
        super(Connection_Client, self).start()
        self.connect()
        self.conn = self


class MainLoopBase(threading.Thread):
    def __init__(self, config, threadName):
        '''This class supplies some '''
        self.config = config
        self.threadName = threadName
        self.eventPool = EventPool(threadName, self.actNoEvent)
        super(MainLoopBase, self).__init__(name=self.threadName)

    def mainLoop(self):
        while True:
            event = self.eventPool.popEvent()
            event['Handler'](**event)

    def actNoEvent(self): pass


class ServerLoop(MainLoopBase):
    def start(self):
        conn = Connection_Server(
            self.config['Connection']['Host'],
            self.config['Connection']['Port'],
            self.eventPool, self.recvHandler)
        conn.start()
        self.mainLoop()

    def recvHandler(self, Data='', Connection=None, EventPool=None):
        print('%s: recv data: %s' % (self.threadName, Data))


class ClientLoop(MainLoopBase):
    def start(self):
        conn = Connection_Client(
            self.config['Connection']['Host'],
            self.config['Connection']['Port'],
            self.eventPool, self.recvHandler)
        conn.start()
        self.mainLoop()

    def recvHandler(self, Data='', Connection=None, EventPool=None):
        print('%s: recv data: %s' % (self.threadName, Data))
