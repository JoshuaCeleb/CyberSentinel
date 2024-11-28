# c2_server.py
import socket
import threading
import json
from datetime import datetime


class C2Server:
    def __init__(self, host="127.0.0.1", port=9999):
        self.host = host
        self.port = port
        self.clients = []
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def start(self):
        self.server_socket.bind((self.host, self.port))
        self.server_socket.listen(5)
        print(f"[*] Listening on {self.host}:{self.port}")
        threading.Thread(target=self.accept_clients, daemon=True).start()

    def accept_clients(self):
        while True:
            client_socket, addr = self.server_socket.accept()
            client_id = len(self.clients) + 1
            self.clients.append({'id': client_id, 'socket': client_socket,
                                'ip': addr[0], 'port': addr[1], 'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')})
            print(f"[*] Client {client_id} connected from {addr[0]}:{addr[1]}")
            threading.Thread(target=self.handle_client, args=(
                client_socket, client_id), daemon=True).start()

    def handle_client(self, client_socket, client_id):
        while True:
            try:
                message = client_socket.recv(4096).decode()
                if not message:
                    break
            except ConnectionResetError:
                break
        client_socket.close()
        self.remove_client(client_id)

    def remove_client(self, client_id):
        self.clients = [
            client for client in self.clients if client['id'] != client_id]
        print(f"[*] Client {client_id} disconnected.")

    def list_clients(self):
        return self.clients

    def close(self):
        self.server_socket.close()


# To run the server:
if __name__ == "__main__":
    c2_server = C2Server()
    c2_server.start()
    while True:
        command = input(
            "Press Enter to keep the server running or type 'exit' to stop:")
        if command == 'exit':
            c2_server.close()
            break
