from flask import Flask, jsonify, request
from flask_cors import CORS
import requests

app = Flask(__name__)
# Bu satır, HTML sitenin sunucuya bağlanmasına izin verir (CORS Çözümü)
CORS(app)

# --- AYARLAR ---
# Buraya en son aldığın veya IP'yi bulduktan sonra alacağın Token'ı yapıştır
TOKEN = "SENİN_TOKEN_BURAYA"
BASE_URL = "https://api.brawlstars.com/v1"
HEADERS = {
    "Authorization": f"Bearer {TOKEN}",
    "Accept": "application/json"
}

# --- SUNUCU IP ADRESİNİ LOGLARA YAZDIRMA ---
# Render'da çalıştırdığında bu kısım sana Supercell'e girmen gereken IP'yi söyleyecek
try:
    sunucu_ip = requests.get('https://api.ipify.org').text
    print("\n" + "="*50)
    print(f"S1 TAG API SUNUCU IP ADRESİ: {sunucu_ip}")
    print("BU IP'YI DEVELOPER PORTAL'A EKLEMEYİ UNUTMA!")
    print("="*50 + "\n")
except Exception as e:
    print(f"IP Adresi sorgulanırken hata oluştu: {e}")

# Yardımcı Fonksiyon: Tag formatını düzeltir (# -> %23)
def format_tag(tag):
    return f"%23{tag.strip().replace('#', '')}"

# --- 1. DURUM KONTROLÜ (IP'yi Tarayıcıda Görmek İçin) ---
@app.route('/')
def status():
    try:
        ip = requests.get('https://api.ipify.org').text
        return jsonify({
            "status": "Online",
            "message": "S1 Tag API Sunucusu Çalışıyor",
            "server_ip": ip
        })
    except:
        return "Sunucu Aktif ama IP alınamadı."

# --- 2. OYUNCU VE BATTLELOG METODU ---
@app.route('/api/player/<tag>', methods=['GET'])
def get_player(tag):
    p_tag = format_tag(tag)
    # Oyuncu Profili
    player_req = requests.get(f"{BASE_URL}/players/{p_tag}", headers=HEADERS)
    # Savaş Günlüğü (Son 25 maç)
    log_req = requests.get(f"{BASE_URL}/players/{p_tag}/battlelog", headers=HEADERS)
    
    if player_req.status_code != 200:
        return jsonify({"error": "Oyuncu bulunamadı", "code": player_req.status_code}), player_req.status_code
        
    return jsonify({
        "info": player_req.json(),
        "battle_log": log_req.json().get('items', [])
    })

# --- 3. KLAN (CLUB) METODLARI ---
@app.route('/api/club/<tag>', methods=['GET'])
def get_club(tag):
    c_tag = format_tag(tag)
    # Klan Genel Bilgileri
    club_req = requests.get(f"{BASE_URL}/clubs/{c_tag}", headers=HEADERS)
    # Klan Üye Listesi
    members_req = requests.get(f"{BASE_URL}/clubs/{c_tag}/members", headers=HEADERS)
    
    if club_req.status_code != 200:
        return jsonify({"error": "Klan bulunamadı"}), club_req.status_code
        
    return jsonify({
        "club_info": club_req.json(),
        "members": members_req.json().get('items', [])
    })

# --- 4. SIRALAMA (RANKINGS) METODLARI ---
@app.route('/api/rankings/<country>/players', methods=['GET'])
def get_player_rankings(country):
    # Örn: country='global' veya 'TR'
    res = requests.get(f"{BASE_URL}/rankings/{country}/players", headers=HEADERS)
    return jsonify(res.json())

# --- 5. ETKİNLİKLER (EVENTS) METODU ---
@app.route('/api/events', methods=['GET'])
def get_events():
    res = requests.get(f"{BASE_URL}/events/rotation", headers=HEADERS)
    return jsonify(res.json())

# --- 6. TÜM KARAKTERLER (BRAWLERS) METODU ---
@app.route('/api/brawlers', methods=['GET'])
def get_brawlers():
    res = requests.get(f"{BASE_URL}/brawlers", headers=HEADERS)
    return jsonify(res.json())

if __name__ == '__main__':
    # Render'da çalışması için port 5000 veya çevre değişkeninden kapaılmalıdır
    import os
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
