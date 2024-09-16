import socket
import json
import tkinter as tk
from tkinter import filedialog, messagebox

# Zmienna globalna do przechowywania ścieżki pliku
file_path_var = None
root = None  # Globalna zmienna dla głównego okna

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

def wake_from_json():
    if file_path_var:
        try:
            with open(file_path_var, 'r', encoding='utf-8') as file:
                data = json.load(file)
                for host in data.get("hosts", []):
                    try:
                        ip_address = host.get("ip_address")
                        mac_address = host.get("mac_address")
                        if ip_address and mac_address:
                            send_magic_packet(mac_address, ip_address)
                        else:
                            print(f"Pominięto host: brakujące IP lub MAC dla {host}")
                    except ValueError as e:
                        print(f"Pominięto host {host}: {e}")

            show_completion_dialog()
        except FileNotFoundError:
            print("Plik nie został znaleziony.")
        except json.JSONDecodeError as e:
            print(f"Błąd dekodowania JSON: {e}")
        except Exception as e:
            print(f"Nieoczekiwany błąd: {e}")
    else:
        print("Ścieżka pliku nie została ustawiona.")

def show_completion_dialog():
    global root
    # Tworzenie nowego okna dialogowego
    dialog = tk.Toplevel()
    dialog.title("Zakończono")

    # Ustawienia rozmiaru okna dialogowego
    dialog.geometry("300x150")

    # Tworzenie napisu
    label = tk.Label(dialog, text="Hosty zostały wybudzone.", font=("Arial", 12))
    label.pack(pady=20)

    # Funkcja do ponownego wybudzenia hostów
    def retry():
        dialog.destroy()
        # Używamy zapisanej ścieżki pliku do ponownego wybudzenia hostów
        wake_from_json()

    # Funkcja do zamknięcia aplikacji
    def exit_app():
        root.destroy()  # Zamyka główne okno aplikacji

    # Tworzenie przycisków
    retry_button = tk.Button(dialog, text="Wybudź jeszcze raz", command=retry, font=("Arial", 12))
    retry_button.pack(side=tk.LEFT, padx=20, pady=10)

    exit_button = tk.Button(dialog, text="Wyjdź", command=exit_app, font=("Arial", 12))
    exit_button.pack(side=tk.RIGHT, padx=20, pady=10)

    # Umożliwienie użytkownikowi zamknięcia okna dialogowego
    dialog.transient(root)
    dialog.grab_set()
    root.wait_window(dialog)

    # Zamknięcie głównego okna aplikacji
    root.destroy()

def select_json_file():
    global file_path_var
    # Otwieramy eksplorator plików z domyślną lokalizacją
    file_path_var = filedialog.askopenfilename(
        title="Wybierz plik JSON",
        filetypes=(("Pliki JSON", "*.json"), ("Wszystkie pliki", "*.*")),
        initialdir="/ścieżka/do/domyślnej/lokalizacji"  # Możesz zmienić na swoją lokalizację
    )

    # Wyświetlamy ścieżkę do wybranego pliku i uruchamiamy funkcję wake_from_json
    if file_path_var:
        print(f"Wybrano plik: {file_path_var}")
        wake_from_json()
    else:
        print("Nie wybrano żadnego pliku")

def main():
    global root
    # Tworzenie głównego okna aplikacji
    root = tk.Tk()
    root.title("Wake On LAN")

    # Ustawienia rozmiaru okna
    root.geometry("400x200")

    # Tworzenie napisu
    label = tk.Label(root, text="Wybudz hosty", font=("Arial", 14))
    label.pack(pady=20)

    # Tworzenie przycisku do wybierania pliku
    button = tk.Button(root, text="Wybierz plik", command=select_json_file, font=("Arial", 12))
    button.pack(pady=10)

    # Uruchomienie głównej pętli aplikacji
    root.mainloop()

if __name__ == "__main__":
    main()
