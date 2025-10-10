# server.py
from flask import Flask, request, jsonify
import paramiko
import os
import tempfile

app = Flask(__name__)
from flask_cors import CORS
CORS(app)


# --- Configuration SFTP pas le test pas le meme identifiant  ---
SFTP_CONFIG = {
    "host": "mft-int.int.kn",
    "port": 22,
    "username": "esr_multiclient",
    "password": "*Esr2024!",
    "remote_dir": "/pub/inbound"
}



@app.route("/upload", methods=["POST"])
def upload():
    try:
        # Vérif : présence du fichier
        if 'file' not in request.files:
            return jsonify({"status": "error", "message": "Aucun fichier reçu"}), 400

        f = request.files["file"]
        filename = f.filename or "unknown.csv"

        # Sauvegarde temporaire
        with tempfile.NamedTemporaryFile(delete=False) as tmp:
            f.save(tmp.name)
            local_path = tmp.name
        print(f"📂 Fichier reçu : {filename} ({os.path.getsize(local_path)} octets)")

        # Connexion SFTP 
        print("🔌 Connexion SFTP en cours...")
        transport = paramiko.Transport((SFTP_CONFIG["host"], SFTP_CONFIG["port"]))
        transport.connect(
            username=SFTP_CONFIG["username"],
            password=SFTP_CONFIG["password"]
        )
        sftp = paramiko.SFTPClient.from_transport(transport)

        # Vérifie que le dossier distant existe
        try:
            sftp.chdir(SFTP_CONFIG["remote_dir"])
        except IOError:
            return jsonify({"status": "error", "message": f"Dossier distant introuvable : {SFTP_CONFIG['remote_dir']}"}), 500

        remote_path = os.path.join(SFTP_CONFIG["remote_dir"], filename)
        print(f"⬆️  Envoi du fichier vers {remote_path} ...")

        # Envoi du fichier
        sftp.put(local_path, remote_path)

        print("✅ Fichier envoyé avec succès !")

        sftp.close()
        transport.close()
        os.remove(local_path)

        return jsonify({"status": "success", "message": f"Fichier envoyé sur le SFTP : {filename}"})

    except Exception as e:
        print("❌ Erreur :", str(e))
        return jsonify({"status": "error", "message": str(e)}), 500


if __name__ == "__main__":
    app.run(debug=True, port=5000)
