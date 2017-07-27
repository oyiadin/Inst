import configparser
import main

config = configparser.ConfigParser()
config.read('config.conf')

while True:
    i = input('> Enter s or c to start a new server/client, blank to exit: ')
    if i =='s':
        main.ServerLoop(config, 'Server').start()
    elif i == 'c':
        main.ClientLoop(config, 'Client').start()
    elif not i:
        break