from flask import Flask, request, jsonify
from flask_cors import CORS 

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

# Data jenis pupuk dan bobotnya
jenis_pupuk = {
    "urea": {"nama": "Urea", "bobot": 0.4},
    "sp36": {"nama": "SP36", "bobot": 0.2},
    "za": {"nama": "ZA", "bobot": 0.15},
    "npk": {"nama": "NPK", "bobot": 0.15},
    "petroganik": {"nama": "Petroganik (Organik)", "bobot": 0.1},
}

# Data jenis tanah dan bobotnya
jenis_tanah = {
    "berpasir": {"nama": "Berpasir", "bobot": 0.1},
    "lempung": {"nama": "Lempung", "bobot": 0.3},
    "liat": {"nama": "Liat", "bobot": 0.25},
    "humus": {"nama": "Humus", "bobot": 0.25},
    "kapur": {"nama": "Kapur", "bobot": 0.1},
}

# Bobot kriteria dalam metode WP
bobot_kriteria = {
    "pupuk": 0.5,
    "tanah": 0.3,
    "produktivitas": 0.1,
    "luas_lahan": 0.1,
}

# Fungsi menghitung skor WP dan dosis pupuk
def hitung_dosis(pupuk_key, tanah_key, produktivitas, luas_lahan):
    # Normalisasi nilai produktivitas dan luas lahan (asumsi maksimal 10)
    norm_produktivitas = produktivitas / 10  
    norm_luas_lahan = luas_lahan / 10  

    nilai_pupuk = jenis_pupuk[pupuk_key]["bobot"]
    nilai_tanah = jenis_tanah[tanah_key]["bobot"]

    # Menghitung skor WP (perkalian nilai pangkat bobot)
    skor = (
        nilai_pupuk ** bobot_kriteria["pupuk"] *
        nilai_tanah ** bobot_kriteria["tanah"] *
        norm_produktivitas ** bobot_kriteria["produktivitas"] *
        norm_luas_lahan ** bobot_kriteria["luas_lahan"]
    )

    # Menghitung dosis (misal maksimum 200 kg/ha)
    dosis = round(skor * 200, 2)

    return dosis

@app.route('/api/rekomendasi_dosis', methods=['POST'])
def rekomendasi_dosis():
    data = request.json
    print("Received data:", data)  # Debug print
    
    pupuk = data.get("pupuk")
    tanah = data.get("tanah")
    produktivitas = float(data.get("produktivitas", 0))
    luas_lahan = float(data.get("luas_lahan", 0))

    print(f"Processing: pupuk={pupuk}, tanah={tanah}, produktivitas={produktivitas}, luas_lahan={luas_lahan}")  # Debug print

    if pupuk not in jenis_pupuk or tanah not in jenis_tanah:
        print(f"Invalid input: pupuk={pupuk in jenis_pupuk}, tanah={tanah in jenis_tanah}")  # Debug print
        return jsonify({"error": "Jenis pupuk atau tanah tidak valid"}), 400

    dosis = hitung_dosis(pupuk, tanah, produktivitas, luas_lahan)
    
    result = {
        "jenis_pupuk": jenis_pupuk[pupuk]["nama"],
        "jenis_tanah": jenis_tanah[tanah]["nama"],
        "produktivitas": produktivitas,
        "luas_lahan": luas_lahan,
        "dosis_rekomendasi_kg_per_ha": dosis
    }
    print("Sending response:", result)  # Debug print
    return jsonify(result)

if __name__ == "__main__":
    app.run(port=5001, debug=True)
