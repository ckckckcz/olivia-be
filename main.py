import streamlit as st
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from pydantic import BaseModel
from typing import Optional
import threading

# FastAPI app for frontend communication
app = FastAPI()

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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

class DosisRequest(BaseModel):
    pupuk: str
    tanah: str
    produktivitas: float
    luas_lahan: float

# FastAPI endpoint
@app.post("/api/rekomendasi_dosis")
async def rekomendasi_dosis(request: DosisRequest):
    try:
        if request.pupuk not in jenis_pupuk or request.tanah not in jenis_tanah:
            return {"error": "Jenis pupuk atau tanah tidak valid"}
        
        dosis = hitung_dosis(
            request.pupuk,
            request.tanah,
            request.produktivitas,
            request.luas_lahan
        )
        
        return {
            "jenis_pupuk": jenis_pupuk[request.pupuk]["nama"],
            "jenis_tanah": jenis_tanah[request.tanah]["nama"],
            "produktivitas": request.produktivitas,
            "luas_lahan": request.luas_lahan,
            "dosis_rekomendasi_kg_per_ha": dosis
        }
    except Exception as e:
        print(f"Error: {str(e)}")
        return {"error": str(e)}

# Streamlit UI
def main():
    st.title("Sistem Rekomendasi Dosis Pupuk")
    
    # Input section
    st.header("Input Data")
    col1, col2 = st.columns(2)
    
    with col1:
        pupuk = st.selectbox(
            "Jenis Pupuk",
            options=list(jenis_pupuk.keys()),
            format_func=lambda x: jenis_pupuk[x]["nama"]
        )
        produktivitas = st.slider(
            "Produktivitas Lahan (Skala 1-10)",
            min_value=0.0,
            max_value=10.0,
            value=5.0,
            step=0.1
        )
    
    with col2:
        tanah = st.selectbox(
            "Jenis Tanah",
            options=list(jenis_tanah.keys()),
            format_func=lambda x: jenis_tanah[x]["nama"]
        )
        luas_lahan = st.slider(
            "Luas Lahan (Skala 1-10 ha)",
            min_value=0.0,
            max_value=10.0,
            value=5.0,
            step=0.1
        )
    
    # Calculate button
    if st.button("Hitung Dosis Pupuk"):
        dosis = hitung_dosis(pupuk, tanah, produktivitas, luas_lahan)
        
        # Results section
        st.header("Hasil Perhitungan")
        col1, col2 = st.columns(2)
        
        with col1:
            st.metric("Dosis Pupuk", f"{dosis:.2f} kg/ha")
            st.info(f"Jenis Pupuk: {jenis_pupuk[pupuk]['nama']}")
        
        with col2:
            total_dosis = dosis * luas_lahan
            st.metric("Total Kebutuhan", f"{total_dosis:.2f} kg")
            st.info(f"Jenis Tanah: {jenis_tanah[tanah]['nama']}")
        
        # Show calculation details
        with st.expander("Detail Perhitungan"):
            st.write("Bobot yang digunakan:")
            st.json({
                "Pupuk": jenis_pupuk[pupuk]["bobot"],
                "Tanah": jenis_tanah[tanah]["bobot"],
                "Produktivitas": produktivitas/10,
                "Luas Lahan": luas_lahan/10
            })

def run_fastapi():
    uvicorn.run(app, host="0.0.0.0", port=5001)

if __name__ == "__main__":
    # Run FastAPI in a separate thread
    api_thread = threading.Thread(target=run_fastapi, daemon=True)
    api_thread.start()
    
    # Run Streamlit
    main()
