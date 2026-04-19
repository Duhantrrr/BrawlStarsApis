from flask import Flask, jsonify, request
from flask_cors import CORS
import requests
import os

app = Flask(__name__)
# Tarayıcıdan (HTML'den) gelen isteklerin engellenmemesi için CORS aktif
CORS(app)

# --- AYARLAR ---
# Yeni verdiğin token buraya işlendi
TOKEN = "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzUxMiIsImtpZCI6IjI4YTMxOGY3LTAwMDAtYTFlYi03ZmExLTJjNzQzM2M2Y2NhNSJ9.eyJpc3MiOiJzdXBlcmNlbGwiLCJhdWQiOiJzdXBlcmNlbGw6Z2FtZWFwaSIsImp0aSI6ImMyMmMxNWE0LTA3ZWYtNGIzOC1hYzczLWY0MWFkNmVjMzAwYSIsImlhdCI6MTc3NjU5MDQxNSwic3ViIjoiZGV2ZWxvcGVyLzdiNjg0ZTYzLTUyYzUtZDM4Yi0zMzAxLTE3MjkxNGVhMDgwNyIsInNjb3BlcyI6WyJicmF3bHN0YXJzIl0sImxpbWl0cyI6W3sidGllciI6ImRldmVsb3Blci9zaWx2ZXIiLCJ0eXBlIjoidGhyb3R0bGluZyJ9LHsiY2lkcnMiOlsiNzQuMjIwLjQ4LjIwMiJdLCJ0eXBlIjoiY2xpZW50In1dfQ.sg0UTi7Q2pjAJNakj_jPmJaRdzsbShmLKpwla1_Tlfd3mBWWip-THI0IbovDyMyKvtpWMHGthYaNQSZBX2VW0Q"
BASE_URL = "https://api.brawlstars.com/v1"
HEADERS = {
    "Authorization": f"Bearer {TOKEN}",
    "Accept": "application/json"
}

# Sunucu IP adresini doğrulamak için (Render loglarında görünür)
try:
    current_ip = requests.get('https://api.ipify.org').text
    print(f"\n--- SUNUCU IP ADRESI: {current_ip} ---")
except:
    pass

def format_tag(tag):
    return f"%23{tag.strip().replace('#', '')}"

# 1. SUNUCU DURUMU (Test için)
@app.route('/')
def home():
    return jsonify({
        "status": "S1 Tag API Aktif",
        "ip_address": "74.220.48.202"
    })

# 2. OYUNCU VE MAÇ GEÇMİŞİ
@app.route('/api/player/<tag>')
def get_player(tag):
    p_tag = format_tag(tag)
    player_res = requests.get(f"{BASE_URL}/players/{p_tag}", headers=HEADERS)
    log_res = requests.get(f"{BASE_URL}/players/{p_tag}/battlelog", headers=HEADERS)
    
    if player_res.status_code != 200:
        return jsonify({"error": "Oyuncu bulunamadı", "status": player_res.status_code}), player_res.status_code
        
    return jsonify({
        "info": player_res.json(),
        "battle_log": log_res.json().get('items', [])
    })

# 3. KLAN BİLGİLERİ VE ÜYELERİ
@app.route('/api/club/<tag>')
def get_club(tag):
    c_tag = format_tag(tag)
    club_res = requests.get(f"{BASE_URL}/clubs/{c_tag}", headers=HEADERS)
    members_res = requests.get(f"{BASE_URL}/clubs/{c_tag}/members", headers=HEADERS)
    
    if club_res.status_code != 200:
        return jsonify({"error": "Klan bulunamadı"}), club_res.status_code
        
    return jsonify({
        "club_info": club_res.json(),
        "members": members_res.json().get('items', [])
    })

# 4. SIRALAMALAR (Oyuncu veya Klan)
@app.route('/api/rankings/<country>/<type>')
def get_rankings(country, type):
    # type: 'players' veya 'clubs' | country: 'global' veya 'TR'
    url = f"{BASE_URL}/rankings/{country}/{type}"
    res = requests.get(url, headers=HEADERS)
    return jsonify(res.json())

# 5. AKTİF ETKİNLİKLER (Harita Rotasyonu)
@app.route('/api/events')
def get_events():
    res = requests.get(f"{BASE_URL}/events/rotation", headers=HEADERS)
    return jsonify(res.json())

# 6. TÜM KARAKTERLER
@app.route('/api/brawlers')
def get_brawlers():
    res = requests.get(f"{BASE_URL}/brawlers", headers=HEADERS)
    return jsonify(res.json())

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
