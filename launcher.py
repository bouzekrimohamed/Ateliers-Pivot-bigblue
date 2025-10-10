import subprocess
import time
import webbrowser
import os
import sys
import tempfile
import shutil

# 🔔 Notification Windows
try:
    from win10toast import ToastNotifier
    toaster = ToastNotifier()
except ImportError:
    toaster = None


def resource_path(relative_path):
    """
    Trouve le bon chemin même après conversion en .exe (PyInstaller)
    """
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)


def main():
    print("🚀 Lancement du serveur BigBlue...")
    server_path = resource_path("server.py")

    # Exécute le serveur Flask en arrière-plan sans console
    subprocess.Popen(
        ["python", server_path],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )

    # Attendre que le serveur démarre
    time.sleep(3)

    # Ouvrir automatiquement ton interface hébergée
    webbrowser.open("https://bouzekrimohamed.github.io/Ateliers-Pivot-bigblue/")

    # Notification Windows (si disponible)
    if toaster:
        icon_path = resource_path("kn.ico") if os.path.exists(resource_path("kn.ico")) else None
        toaster.show_toast(
            "BigBlue – ESR_ST",
            "✅ Serveur SFTP lancé avec succès.\nL’outil est prêt à l’emploi !",
            icon_path=icon_path,
            duration=5,
            threaded=True,
        )

    # Maintient un peu l’application active pour éviter la fermeture immédiate
    time.sleep(2)

    # Nettoyage du dossier temporaire (_MEIxxxx)
    try:
        tempdir = getattr(sys, '_MEIPASS', tempfile.gettempdir())
        shutil.rmtree(tempdir, ignore_errors=True)
    except Exception:
        pass

    print("✅ Mohamed's Launcher terminé proprement.")


if __name__ == "__main__":
    main()
