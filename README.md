# BadUSB Python Script

Skrypt Python udający urządzenie BadUSB, który automatycznie przesyła zebrane dane na Twój serwer Discord za pomocą Webhooka. Projekt zawiera gotowe instrukcje kompilacji do pliku wykonywalnego `.exe` oraz szybkiego uruchomienia.

## 🚀 Wymagania wstępne

Przed rozpoczęciem upewnij się, że masz zainstalowany:
* **Python 3.x**
* **PyInstaller** (narzędzie do kompilacji)

## 🛠️ Instrukcja konfiguracji i uruchomienia

### Krok 1: Konfiguracja Webhooka Discord
1. Otwórz kod źródłowy skryptu w edytorze tekstowym.
2. Znajdź zmienną odpowiedzialną za adres URL webhooka (np. `WEBHOOK_URL`).
3. Wklej tam swój wygenerowany link do webhooka z Discorda.

### Krok 2: Instalacja PyInstallera
Jeśli jeszcze nie posiadasz narzędzia PyInstaller, zainstaluj je za pomocą menedżera pakietów pip:
```bash
pip install pyinstaller
```

### Krok 3: Kompilacja do pliku `.exe`
Aby skompilować skrypt do jednego, niezależnego pliku `.exe` (który nie wyświetla czarnego okna konsoli podczas działania), użyj poniższej komendy:
```bash
pyinstaller --onefile --noconsole nazwa_skryptu.py
```
*Po zakończeniu procesu gotowy plik znajdziesz w nowo utworzonym folderze `dist`.*

### Krok 4: Uruchomienie w PowerShell
Aby szybko przetestować i uruchomić wygenerowany plik bezpośrednio z poziomu konsoli PowerShell, przejdź do folderu `dist` i wykonaj:
```powershell
Start-Process .\nazwa_skryptu.exe
```

## ⚠️ Zastrzeżenie (Disclaimer)

Projekt został stworzony wyłącznie w celach edukacyjnych i testów penetracyjnych za zgodą właściciela infrastruktury. Autor nie ponosi odpowiedzialności za jakiekolwiek szkody wyrządzone przez niewłaściwe użycie tego oprogramowania.
