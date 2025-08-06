from flask import Flask, request, jsonify
import requests
import json
import os

print("🚀 Memulai aplikasi... import selesai.")

app = Flask(__name__)

INSTANCE_ID = 'instance137646'
TOKEN = 'jmitcigiqnheius8'

def load_jadwal():
    try:
        with open('jadwal.json', 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return {}

def save_jadwal(jadwal):
    with open('jadwal.json', 'w') as f:
        json.dump(jadwal, f, indent=4)

@app.route('/webhook', methods=['POST'])
def webhook():
    try:
        payload = request.json
        print("📥 Data masuk:", payload)

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
        print("❌ Error saat webhook:", e)
        return jsonify({"error": str(e)}), 500

def send_message(to, message):
    url = f"https://api.ultramsg.com/{INSTANCE_ID}/messages/chat?token={TOKEN}"
    headers = {"Content-Type": "application/json"}
    payload = {"to": to, "body": message}
    response = requests.post(url, json=payload, headers=headers)
    print("📤 Response Ultramsg:", response.text)

if __name__ == '__main__':
    try:
        print("✅ Modul berhasil diimport.")
        port = int(os.environ.get("PORT", 5000))
        app.run(host='0.0.0.0', port=port)
        print(f"✅ Flask berjalan di port {port}")
    except Exception as e:
        print("❌ Error saat menjalankan app:", e)
