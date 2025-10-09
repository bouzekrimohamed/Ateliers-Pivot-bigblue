from flask import Flask, request
import paramiko
import os
import traceback

app = Flask(__name__)

@app.route("/upload", methods=["POST"])
def upload():
    # Vérifie la présence du fichier
    if 'file' not in request.files:
        return "❌ Aucun fichier reçu", 400

    f = request.files["file"]
    local_path = f.filename

    try:
        # Sauvegarde temporaire du fichier
        f.save(local_path)
        print(f"📂 Fichier reçu : {local_path} ({os.path.getsize(local_path)} octets)")

        # --- CONFIG SFTP ---
        host = "mft-int.int.kn"        # 🔧 serveur réel de prod
        port = 22
        username = "esr_multiclient"
        password = "*Esr2024!"         # ⚠️ à vérifier si c’est bien le mot de passe actif
        remote_path = f"/pub/inbound/{local_path}"

        # --- CONNEXION SFTP ---
        print(f"🔌 Connexion SFTP vers {host}:{port} ...")
        transport = paramiko.Transport((host, port))
        transport.connect(username=username, password=password)
        sftp = paramiko.SFTPClient.from_transport(transport)

        # --- ENVOI DU FICHIER ---
        print(f"⬆️ Envoi du fichier vers {remote_path} ...")
        sftp.put(local_path, remote_path)
        print("✅ Fichier transféré avec succès !")

        # --- FERMETURE ---
        sftp.close()
        transport.close()

        # --- NETTOYAGE ---
        if os.path.exists(local_path):
            os.remove(local_path)

        return "✅ Fichier envoyé avec succès sur le SFTP", 200

    except Exception as e:
        print("💥 Erreur SFTP :", str(e))
        traceback.print_exc()

        # Nettoyage du fichier temporaire s’il existe
        if os.path.exists(local_path):
            os.remove(local_path)

        return f"❌ Erreur SFTP : {str(e)}", 500


if __name__ == "__main__":
    # Serveur HTTPS local pour éviter le blocage GitHub Pages (Mixed Content)
    print("🚀 Serveur Flask lancé sur https://localhost:5000 (HTTPS activé)")
    app.run(debug=True, port=5000, ssl_context='adhoc')
