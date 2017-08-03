import queue
import json
import time
import interface
import listen
from config import *
from common import *


pool = queue.Queue()
users = []  # ID, PubKey, addr, pool
ID = gen_ID()


def main_loop():
    # interface.init(pool)
    listen.ListeningThread(pool, ID).start()
    if config['Connection']['EnableSuperHost'] == 'Yes':
        host, port = config['Connection']['SuperHost'].split(':')
        conn = connection.ConnectionThread(ID, addr=(host, port))
        conn.start()
        to_send = gen_dict(Action='RequestUsersList', ID=ID, IDTo='#'*12)
        conn.pool.put(gen_dict(Action='Send', Data=json.dumps(to_send)))

    else:
        pass

    while True:
        event = pool.get() if not pool.empty() else None

        if not event: pass

        elif event['Action'] == 'NewData':
            data = json.loads(event['Data'])

            if data['first_data']:  # if new user, append it to the users-list
                users.append(gen_dict(ID=data['ID'], PubKey=data['PubKey'],
                    addr=data['addr'], pool=data['pool']))

            if data['InstVersion'] != '0.1': pass

            if data['Action'] == 'RequestUsersList':
                if (data['IDTo'] == '#'*12) or (data['IDTo'] == ID):
                    user20 = random.sample(users, 20) if len(users)>20 \
                        else users
                    user20 = [
                        {'ID':i['ID'], 'PubKey':i['Pubkey'], 'addr':i['addr']} \
                            for i in user20]  # only needs ID, PubKey and addr
                    to_send = gen_dict(Action=UsersList, ID=ID, List=user20)
                    data['pool'].put(gen_dict(
                        Action='Send',
                        Data=json.dumps(to_send)))
                else:
                    pass


if __name__ == '__main__':
    main_loop()