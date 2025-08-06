from flask import Flask, request, jsonify
import requests
import json
import os

app = Flask(__name__)

# Ganti dengan milikmu
INSTANCE_ID = 'instance137646'
TOKEN = 'jmitcigiqnheius8'

# File lokasi di Railway (file storage terbatas)
JADWAL_PATH = '/tmp/jadwal.json'

# Load data jadwal dari file
def load_jadwal():
    try:
        if not os.path.exists(JADWAL_PATH):
            with open(JADWAL_PATH, 'w') as f:
                json.dump({
                    "18.00": "", "19.00": "", "20.00": ""
                }, f)
        with open(JADWAL_PATH, 'r') as f:
            return json.load(f)
    except Exception as e:
        print("Error load_jadwal:", e)
        return {}

# Simpan jadwal ke file
def save_jadwal(jadwal):
    try:
        with open(JADWAL_PATH, 'w') as f:
            json.dump(jadwal, f, indent=4)
    except Exception as e:
        print("Error save_jadwal:", e)

# Untuk root endpoint biar nggak error 502
@app.route("/", methods=['GET'])
def home():
    return "Bot Futsal Aktif ✅"

# Endpoint webhook dari Ultramsg
@app.route('/webhook', methods=['POST'])
def webhook():
    try:
        payload = request.json
        print("DATA MASUK:", payload)

        data = payload.get('data', {})
        msg = data.get('body', '').lower()
        sender = data.get('from', '')

        if not msg or not sender:
            return jsonify({"error": "Missing message or sender"}), 400

        jadwal = load_jadwal()
        response = ""

        if "jadwal" in msg:
            response = "📅 Jadwal tersedia:\n"
            for jam, nama in jadwal.items():
                status = "✅ Tersedia" if not nama else f"❌ Sudah dibooking oleh {nama}"
                response += f"- {jam}: {status}\n"

        elif "book" in msg:
            for jam in jadwal:
                if jam in msg and not jadwal[jam]:
                    nama_tim = msg.split("atas nama")[-1].strip().title()
                    jadwal[jam] = nama_tim
                    save_jadwal(jadwal)
                    response = f"✅ Booking berhasil untuk jam {jam} atas nama {nama_tim}!"
                    break
            else:
                response = "❌ Jam tersebut tidak tersedia atau sudah dibooking."

        else:
            response = (
                "⚽ Halo! Ketik *jadwal* untuk melihat jadwal lapangan,\n"
                "atau ketik *book 18.00 atas nama Tim Kamu* untuk booking."
            )

        send_message(sender, response)
        return jsonify({"status": "ok"})
    
    except Exception as e:
        print("ERROR WEBHOOK:", str(e))
        return jsonify({"error": str(e)}), 500


# Kirim balasan ke WA
def send_message(to, message):
    url = f"https://api.ultramsg.com/{INSTANCE_ID}/messages/chat?token={TOKEN}"
    headers = {"Content-Type": "application/json"}
    payload = {"to": to, "body": message}
    try:
        response = requests.post(url, json=payload, headers=headers)
        print("ULTRAMSG:", response.text)
    except Exception as e:
        print("Send message failed:", e)

# Jalankan di Railway
if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)

