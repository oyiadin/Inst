import hashlib
import random

__all__ = ['gen_dict', 'gen_ID']


def gen_dict(**argvs):
    if not argvs.get('InstVersion'):
        argvs['InstVersion'] = 0.1
    return argvs


def gen_ID():
    CHARS = 'ABCDEFGHJKLMNPQRTWXYabcdefghikmnopqrstuvwxyz0123456789+-=#@/'
    while True:
        ID = ''
        for i in range(12):
            ID += random.choice(CHARS)
        if hashlib.md5(ID.encode()).hexdigest().startswith('00000'):
            return ID
