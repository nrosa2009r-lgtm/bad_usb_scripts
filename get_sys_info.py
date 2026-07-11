import winreg

def get_win_build():

    try:
        reg_key = winreg.OpenKey(
            winreg.HKEY_LOCAL_MACHINE,r"SOFTWARE\Microsoft\Windows NT\CurrentVersion"
        )

        build_num, _ = winreg.QueryValueEx(reg_key,"CurrentBuild")
        winreg.CloseKey(reg_key)

        return build_num
    
    except Exception as e:
        return f"Error:   {e}"
    



print(get_win_build())