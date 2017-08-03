import queue
import listen


conns = []
pool = queue.Queue()
listen.ListeningThread(pool).run()

while True:
	event = pool.get() if not pool.empty() else None

	if not event: pass

	elif event['Action'] == 'NewConn':
		conn, addr = event['Object'], event['Addr']
		conns[addr] = conn

	elif event['Action'] == 'NewData':
		data = event['Data']
		