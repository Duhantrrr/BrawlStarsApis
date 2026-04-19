from flask import Flask, jsonify, request
from flask_cors import CORS
import requests

app = Flask(__name__)
CORS(app)  # Domaininden gelen isteklere izin verir

# --- AYARLAR ---
TOKEN = "SENİN_ÇALIŞAN_TOKENIN"
BASE_URL = "https://api.brawlstars.com/v1"
HEADERS = {
    "Authorization": f"Bearer {TOKEN}",
    "Accept": "application/json"
}

# Yardımcı Fonksiyon: Etiketi API formatına getirir (# -> %23)
def format_tag(tag):
    return f"%23{tag.strip().replace('#', '')}"

# --- 1. OYUNCU METODLARI ---

@app.route('/api/player/<tag>', methods=['GET'])
def get_player_full(tag):
    """Oyuncu profili ve son 25 maçını birlikte getirir."""
    p_tag = format_tag(tag)
    
    # Profil verisi
    player_req = requests.get(f"{BASE_URL}/players/{p_tag}", headers=HEADERS)
    # Maç geçmişi (Battlelog)
    log_req = requests.get(f"{BASE_URL}/players/{p_tag}/battlelog", headers=HEADERS)
    
    if player_req.status_code != 200:
        return jsonify({"error": "Oyuncu bulunamadı"}), player_req.status_code
        
    return jsonify({
        "info": player_req.json(),
        "battle_log": log_req.json().get('items', [])
    })

# --- 2. KLAN (CLUB) METODLARI ---

@app.route('/api/club/<tag>', methods=['GET'])
def get_club(tag):
    """Klan bilgilerini ve klan üyelerini getirir."""
    c_tag = format_tag(tag)
    
    # Klan genel bilgileri
    club_req = requests.get(f"{BASE_URL}/clubs/{c_tag}", headers=HEADERS)
    # Klan üyeleri
    members_req = requests.get(f"{BASE_URL}/clubs/{c_tag}/members", headers=HEADERS)
    
    if club_req.status_code != 200:
        return jsonify({"error": "Klan bulunamadı"}), club_req.status_code
        
    return jsonify({
        "club_info": club_req.json(),
        "members": members_req.json().get('items', [])
    })

# --- 3. SIRALAMA (RANKINGS) METODLARI ---

@app.route('/api/rankings/<country>/players', methods=['GET'])
def get_player_rankings(country):
    """Ülke bazlı veya küresel oyuncu sıralaması (country='global' veya 'TR')."""
    res = requests.get(f"{BASE_URL}/rankings/{country}/players", headers=HEADERS)
    return jsonify(res.json())

@app.route('/api/rankings/<country>/clubs', methods=['GET'])
def get_club_rankings(country):
    """Ülke bazlı veya küresel klan sıralaması."""
    res = requests.get(f"{BASE_URL}/rankings/{country}/clubs", headers=HEADERS)
    return jsonify(res.json())

# --- 4. ETKİNLİK (EVENTS) METODLARI ---

@app.route('/api/events', methods=['GET'])
def get_events():
    """Şu an aktif olan haritaları ve modları getirir."""
    res = requests.get(f"{BASE_URL}/events/rotation", headers=HEADERS)
    return jsonify(res.json())

# --- 5. BRAWLERS (KARAKTERLER) ---

@app.route('/api/brawlers', methods=['GET'])
def get_all_brawlers():
    """Oyundaki tüm karakterlerin listesini ve özelliklerini getirir."""
    res = requests.get(f"{BASE_URL}/brawlers", headers=HEADERS)
    return jsonify(res.json())

# --- SERVER BAŞLATMA ---

if __name__ == '__main__':
    # Geliştirme aşamasında debug=True, yayına alırken False yapmalısın.
    app.run(host='0.0.0.0', port=5000, debug=True)
