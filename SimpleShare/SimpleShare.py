import socket
import argparse
import json
import os
import os.path
from tkinter import W

class Client:
    def __init__(self, cs):
        self.cs = cs 

    def recv_exact(self, amount):
        out = []
        while amount > 0:
            chunk = self.cs.recv(amount)
            out.append(chunk)
            amount -= len(chunk)
        return b''.join(out)

    def send(self, data):
        sent = 0
        while sent < len(data):
            amount = self.cs.send(data[sent:])
            sent += amount

    def close(self):
        self.cs.close()

class Service:
    def enum_path(self, path):
        nodes = os.listdir(path)
        for node in nodes:
            fnode = os.path.join(path, node)
            if os.isdir(fnode):
                for item in self.enum_path(fnode):
                    yield item
            else:
                yield fnode

    def enum_paths(self):
        for path in self.paths:
            for item in self.enum_path(path):
                yield item

    def directive_list(self, client):
        paths = list(self.enum_paths())
        data = json.dumps(paths).encode('utf8')
        client.send(data)

    def transmit_path(self, client, path):
        with open(path, 'rb') as fd:
            while True:
                chunk = fd.read(1024 * 1024)
                if len(chunk) == 0: break 
                client.send(chunk)

    def directive_pull(self, client, path):
        for path in self.enum_paths():
            if path == path:
                self.transmit_path(client, path)

    def __init__(self, host, port, paths):
        self.paths = paths
        self.host = host
        self.port = port
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.s.bind((host, port))

        def serve_forever(self):
            self.s.listen()
            while True:
                print('waiting for client')
                client = Client(self.s.accept())
                print('handling client')
                cmd = json.loads(client.recv_exact(1024).decode('utf8'))
                directive = cmd['directive']
                if directive == 'list':
                    self.directive_list(client)
                elif directive == 'pull':
                    self.directive_pull(client, cmd['path'])
                else:
                    pass
                client.close()

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