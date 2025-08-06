from flask import Flask, request, jsonify
import requests
import json

app = Flask(__name__)

INSTANCE_ID = 'instance137646'  # ganti dengan milikmu
TOKEN = 'jmitcigiqnheius8'          # ganti dengan milikmu

# Load data jadwal
def load_jadwal():
    with open('jadwal.json') as f:
        return json.load(f)

# Simpan data jadwal
def save_jadwal(jadwal):
    with open('jadwal.json', 'w') as f:
        json.dump(jadwal, f, indent=4)

@app.route('/webhook', methods=['POST'])
def webhook():
    payload = request.json
    print("DATA MASUK:", payload)

    if 'data' not in payload:
        return jsonify({"error": "Invalid payload"}), 400

    msg = payload['data'].get('body', '').lower()
    sender = payload['data'].get('from', '')

    if not msg or not sender:
        return jsonify({"error": "Missing data"}), 400

    # Load jadwal
    jadwal = load_jadwal()
    response = ""

    if "jadwal" in msg:
        response = "📅 Jadwal tersedia:\n"
        for jam in jadwal:
            status = "✅ Tersedia" if not jadwal[jam] else f"❌ Sudah dibooking oleh {jadwal[jam]}"
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
        response = "⚽ Halo! Ketik *jadwal* untuk melihat jadwal lapangan,\natau ketik *book 18.00 atas nama Tim Kamu* untuk booking."

    # Kirim ke WhatsApp
    send_message(sender, response)
    return jsonify({"status": "ok"})


def send_message(to, message):
    url = f"https://api.ultramsg.com/{INSTANCE_ID}/messages/chat?token={TOKEN}"
    headers = {"Content-Type": "application/json"}
    payload = {
        "to": to,
        "body": message
    }
    response = requests.post(url, json=payload, headers=headers)
    print("RESPON ULTRAMSG:", response.text)

if __name__ == '__main__':
    app.run(debug=True)


