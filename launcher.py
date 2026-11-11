import logging
import os
import threading
import time
import traceback
import webbrowser
from pathlib import Path
from tkinter import Tk, messagebox

def log_path():
    root = Path(os.environ.get("LOCALAPPDATA", Path.home())) / "AdvertisingPrintERP"
    root.mkdir(parents=True, exist_ok=True)
    return root / "startup.log"

def open_browser():
    time.sleep(2)
    webbrowser.open("http://127.0.0.1:8765")

def main():
    try:
        # Explicit import is essential: PyInstaller cannot reliably detect
        # modules loaded only from a string such as "app.main:app".
        from app.main import app
        threading.Thread(target=open_browser, daemon=True).start()
        import uvicorn
        uvicorn.run(app, host="127.0.0.1", port=8765, log_level="info")
    except Exception:
        details = traceback.format_exc()
        path = log_path()
        path.write_text(details, encoding="utf-8")
        try:
            root = Tk()
            root.withdraw()
            messagebox.showerror(
                "تعذر تشغيل نظام المطبعة",
                "حدث خطأ أثناء تشغيل البرنامج.\n"
                "تم حفظ تفاصيل الخطأ في:\n" + str(path)
            )
            root.destroy()
        except Exception:
            pass

if __name__ == "__main__":
    main()
