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

    # Envoi SFTP
    host = "mft-int-test.int.kn"
    port = 22
    username = "esr_multiclient"
    password = "!2024Esr"
    remote_path = f"/pub/inbound/{local_path}"

    try:
        transport = paramiko.Transport((host, port))
        transport.connect(username=username, password=password)
        sftp = transport.open_sftp()
        sftp.put(local_path, remote_path)
        sftp.close()
        transport.close()
        os.remove(local_path)  # Nettoyage
        return "✅ Fichier envoyé avec succès sur le SFTP"
    except Exception as e:
        os.remove(local_path)
        print(f"SFTP Error: {str(e)}")  # Ajout de logging pour debug
        return f"Erreur SFTP: {str(e)}", 500

if __name__ == "__main__":
    app.run(debug=True, port=5000, ssl_context='adhoc')