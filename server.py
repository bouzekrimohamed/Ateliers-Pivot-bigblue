from flask import Flask, request
import paramiko
import os

app = Flask(__name__)

@app.route("/upload", methods=["POST"])
def upload():
    if 'file' not in request.files:
        return "Aucun fichier reçu", 400

    f = request.files["file"]
    local_path = f.filename
    f.save(local_path)
    print(f"📂 Fichier reçu : {local_path} ({os.path.getsize(local_path)} octets)")

    # --- Envoi SFTP ---
    host = "mft-int-test.int.kn"
    port = 22
    username = "esr_multiclient"
    password = "!2024Esr"
    remote_path = f"/pub/inbound/{local_path}"

    try:
        # Connexion SFTP
        transport = paramiko.Transport((host, port))
        transport.connect(username=username, password=password)
        sftp = transport.open_sftp()

        # Envoi du fichier
        sftp.put(local_path, remote_path)

        # Fermeture
        sftp.close()
        transport.close()

        # Suppression du fichier local
        os.remove(local_path)

        return "✅ Fichier envoyé avec succès sur le SFTP"

    except Exception as e:
        # Nettoyage si erreur
        if os.path.exists(local_path):
            os.remove(local_path)
        return f"Erreur SFTP: {str(e)}", 500


if __name__ == "__main__":
    app.run(debug=True, port=5000)
