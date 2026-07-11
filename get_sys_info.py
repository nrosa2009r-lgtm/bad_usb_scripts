import winreg

def get_win_build():

    try:
        key = winreg.OpenKey(
            winreg.HKEY_LOCAL_MACHINE,r"SOFTWARE\Microsoft\Windows NT\CurrentVersion"
        )

        product_name, _ = winreg.QueryValueEx(key, "ProductName")
        display_version, _ = winreg.QueryValueEx(key, "DisplayVersion") # np. 23H2
        current_build, _ = winreg.QueryValueEx(key, "CurrentBuild")     # np. 22631
        
        try:
            # UBR to numer poprawki po kropce (np. .3527)
            ubr, _ = winreg.QueryValueEx(key, "UBR")
            full_build = f"{current_build}.{ubr}"
        except FileNotFoundError:
            full_build = current_build

        winreg.CloseKey(key)
        
        # Korekta nazwy dla Windows 11 (rejestr często zwraca "Windows 10", mimo że to 11)
        if int(current_build) >= 22000 and "Windows 10" in product_name:
            product_name = product_name.replace("Windows 10", "Windows 11")

        return {
            "Nazwa": product_name,
            "Wersja": display_version,
            "Kompilacja": full_build
        }
        
    except Exception as e:
        return f"Błąd: {e}"
    








    

# Wyświetlenie wyników
info = get_win_build()
if isinstance(info, dict):
    print(f"System: {info['Nazwa']}")
    print(f"Wersja: {info['Wersja']}")
    print(f"Pełny build: {info['Kompilacja']}")
else:
    print(info)