import socket
import argparse
import json
import os
import os.path
import winsound
import hashlib
import struct

def main():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind(('0.0.0.0', 22555))
    s.listen() 

    while True:
        cs, addr = s.accept()

        out = []
        amount = 0
        while amount < 8:
            chunk = cs.recv(8 - amount)
            if len(chunk) == 0: break
            out.append(chunk)
            amount += len(chunk)
        out = b''.join(out)
        sz = struct.unpack('<Q', out)[0]

        out = []
        amount = 0
        while amount < sz:
            chunk = cs.recv(1024 * 1024)
            if len(chunk) == 0: break
            out.append(chunk)
            amount += len(chunk)
        out = b''.join(out)

        h = hashlib.sha1()
        h.update(out)
        print('The hash of the WAVE data is %s.' % h.hexdigest())
        print('The size of the data is %s.' % len(out))
        print(out[0:20])

        try:
            winsound.PlaySound(out, winsound.SND_MEMORY)
            print('Done playing sound.')
        except Exception as e:
            print(type(e), e)

        cs.send(b'APPLE')
        cs.close()

if __name__ == '__main__':
    main()