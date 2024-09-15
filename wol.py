import socket
import json
import argparse

def create_magic_packet(macaddress):
    macaddress = macaddress.replace(":", "").replace("-", "").replace(".", "")
    if len(macaddress) != 12:
        raise ValueError("Nieprawidłowy adres MAC.")
    mac_bytes = bytes.fromhex(macaddress)
    magic_packet = b'\xFF' * 6 + mac_bytes * 16
    return magic_packet

def send_magic_packet(macaddress, ip_address):
    packet = create_magic_packet(macaddress)
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        sock.sendto(packet, (ip_address, 9))
        print(f"Magic packet wysłany do: {macaddress} ({ip_address})")

def wake_from_json(json_file):
    with open(json_file, 'r') as file:
        data = json.load(file)
        for host in data.get("hosts", []):
            try:
                ip_address = host.get("ip_address")
                mac_address = host.get("mac_address")
                # Ignorowanie innych danych
                if ip_address and mac_address:
                    send_magic_packet(mac_address, ip_address)
                else:
                    print(f"Pominięto host: brakujące IP lub MAC dla {host}")
            except ValueError as e:
                print(f"Pominięto host {host}: {e}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Wake on LAN z pliku JSON')
    parser.add_argument('json_file', metavar='JSON_FILE', type=str,
                        help='Plik JSON zawierający adresy IP i MAC komputerów do wybudzenia')
    args = parser.parse_args()

    wake_from_json(args.json_file)
