import json
import socket

COMMANDS = '\n'.join(['/join <server_ip_add> <port>', '/leave', '/register <handle>', '/all <message>', '/msg <handle> <message>'])

class OurClient:
    def __init__(self, host=socket.gethostname(), port=12345):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM) # UDP Datagram
        self.join(host, port)
        self.handle = None
    
    def request(self, message):
        self.sock.sendto(message, (self.host, self.port))
        response, ip_add = self.sock.recvfrom(1024)
        return self.deserialize(response)
    
    def join(self, host, port): # TODO
        self.host = host
        self.port = port

    def leave(self): # TODO
        self.sock.close()
    
    def register(self, handle):
        resp = self.request(self.serialize({'command': 'register', 'handle': handle}))
        if resp.strip('\"') == f'Welcome {handle}!':
            self.handle = handle
        return resp
    
    def msg_all(self, sender, message):
        return self.request(self.serialize({'command': 'all', 'sender': sender, 'message': message}))
    
    def msg(self, sender, recipient, message):
        return self.request(self.serialize({'command': 'msg', 'sender': sender, 'recipient': recipient, 'message': message}))

    def serialize(self, dict):
        val = bytes(json.dumps(dict), 'utf-8')
        return val

    def deserialize(self, data):
        val = json.loads(data.decode('utf-8'))
        return val
    
    def read_cmd(self, command):
        cmd, *args = command.split(' ')
        params_err = 'Error: Command parameters do not match or is not allowed.'
        if cmd == '/?':
            if args: print(params_err)
            else: print('\n'.join(COMMANDS))
        elif cmd == '/join':
            if len(args) > 2: print(params_err)
            else:
                if args: self.join(args[0], int(args[1]))
                print(self.request(self.serialize({'command': 'join'})))
        elif cmd == '/leave':
            if args: print(params_err)
            else: print(self.request(self.serialize({'command': 'leave'})))
        elif cmd == '/register':
            if len(args) != 1: print(params_err)
            else: 
                print(self.register(args[0]))
        elif cmd == '/all': #
            pass
        elif cmd == '/msg': #TODO
            pass
        else:
            print('Error: Command not found.')

if __name__ == '__main__':
    serv, acc = False, False
    print('Use /? for a list of commands.')
    client = None

    while True:
        try:
            cmd = input('Enter a command: ')
            if cmd == '/?':
                print(COMMANDS)
            elif client == None and not cmd.startswith('/join'):
                print('Error: You must join a server first.')
            elif cmd.startswith('/join') and client == None:
                client = OurClient()
                client.read_cmd(cmd)
            elif client:
                if client.handle == None and not cmd.startswith('/register'):
                    print('Error: You must register a handle first.')
                else:
                    client.read_cmd(cmd)
        except socket.error as err:
            print(f'Error: {err}')