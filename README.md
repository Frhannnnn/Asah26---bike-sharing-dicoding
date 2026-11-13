# Bike Sharing Data Analysis & Dashboard 🚲

Proyek ini menganalisis pola penyewaan sepeda dari **Bike Sharing Dataset** (Capital Bikeshare, Washington D.C., 2011–2012) mulai dari *Data Wrangling*, *Exploratory Data Analysis (EDA)*, *Explanatory Visualization*, hingga *Advanced Analysis* (Clustering menggunakan *Manual Grouping* & *Binning*), serta menyajikannya dalam bentuk dashboard interaktif menggunakan **Streamlit**.

## Struktur Direktori
```text
submission/
├── dashboard/
│   ├── dashboard.py
│   ├── hour_data.csv
│   └── main_data.csv
├── data/
│   ├── Readme.txt
│   ├── day.csv
│   └── hour.csv
├── notebook.ipynb
├── README.md
├── requirements.txt
└── url.txt
```

## Cara Menjalankan Dashboard di Lokal
1. Pastikan Python 3.9+ sudah terinstal, lalu masuk ke direktori `submission`:
   ```bash
   cd submission
   ```
2. Instal seluruh library yang dibutuhkan:
   ```bash
   pip install -r requirements.txt
   ```
3. Jalankan dashboard Streamlit:
   ```bash
   streamlit run dashboard/dashboard.py
   ```
4. Buka tautan lokal yang muncul di terminal (biasanya `http://localhost:8501`) pada browser Anda.
