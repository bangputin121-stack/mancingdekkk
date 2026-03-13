# 🎣 FISHING WORLD - Telegram Bot Game

Bot game memancing berbasis Python untuk Telegram dengan sistem lengkap.

## 🐟 Fitur Lengkap

### 🎮 Gameplay
- **30+ Jenis Ikan** dengan 7 tingkat rarity (Common → Divine)
- **7 Joran** berbeda dari Bambu hingga Joran Ilahi
- **7 Jenis Umpan** dengan bonus berbeda
- **6 Lokasi Memancing** yang bisa dibuka
- **Sistem Cooldown** berdasarkan lokasi & joran
- **Level & XP** dengan 100+ level

### 🛒 Toko & Economy
- Beli joran, umpan, boost
- Upgrade joran hingga level 20
- Market jual/beli ikan antar pemain
- Transfer ikan ke pemain lain
- Sistem VIP (Bronze/Silver/Gold/Platinum)
- Top Up koin

### 📊 Fitur Lainnya
- Boost aktif (Luck, Rare, XP, Koin)
- Hadiah harian
- Koleksi & Favorit ikan
- Leaderboard (Koin, Level, Tangkapan, Penghasilan)
- Histori tangkapan
- Event berkala

---

## 🚀 Deploy ke Railway + GitHub

### 1. Buat Bot di BotFather
1. Buka Telegram, cari `@BotFather`
2. Ketik `/newbot`
3. Ikuti instruksi, dapatkan **BOT_TOKEN**

### 2. Push ke GitHub
```bash
git init
git add .
git commit -m "Initial commit"
git remote add origin https://github.com/USERNAME/REPO_NAME.git
git push -u origin main
```

### 3. Deploy ke Railway
1. Buka [railway.app](https://railway.app)
2. Klik **New Project** → **Deploy from GitHub Repo**
3. Pilih repo ini
4. Masuk ke **Variables** tab
5. Tambahkan environment variable:
   ```
   BOT_TOKEN = TOKEN_DARI_BOTFATHER
   ```
6. Railway akan otomatis build dan deploy!

### 4. Pastikan Worker Aktif
- Di Railway dashboard, pastikan **worker** service berjalan
- Bot akan otomatis restart jika crash

---

## ⚙️ Environment Variables

| Variable | Keterangan | Contoh |
|----------|-----------|--------|
| `BOT_TOKEN` | Token dari BotFather | `1234567890:ABC...` |
| `DB_PATH` | Path database (opsional) | `fishing_game.db` |

---

## 📁 Struktur File

```
fishing_bot/
├── main.py                    # Entry point
├── requirements.txt           # Dependencies
├── Procfile                   # Railway config
├── railway.toml               # Railway config
├── data/
│   ├── fish_data.py          # Data ikan & rarity
│   └── shop_data.py          # Data toko, maps, VIP
├── database/
│   └── db.py                 # Database SQLite
├── handlers/
│   └── commands.py           # Semua command & callback
└── utils/
    ├── fishing_engine.py     # Logic memancing
    ├── keyboards.py          # Inline keyboards
    └── formatters.py         # Format pesan
```

---

## 🐟 Daftar Rarity Ikan

| Rarity | Chance | Emoji | Contoh Ikan |
|--------|--------|-------|-------------|
| Common | ~40% | ⬜ | Lele, Nila, Gurame |
| Uncommon | ~25% | 🟩 | Bawal, Gabus, Patin |
| Rare | ~18% | 🟦 | Toman, Arwana, Kakap |
| Epic | ~10% | 🟪 | Layaran, Hiu Paus Mini |
| Legendary | ~5% | 🟧 | Arwana Super Red, Naga |
| Mythic | ~1.5% | 🔴 | Leviathan, Naga Laut |
| Divine | ~0.5% | ✨ | Dewa Laut, Raja Samudra |

---

## 💡 Kustomisasi

### Ganti Link Grup/Channel
Edit di `handlers/commands.py`:
```python
GROUP_LINK = "https://t.me/your_group"
CHANNEL_LINK = "https://t.me/your_channel"
```

### Tambah Admin
```python
ADMIN_IDS = [123456789, 987654321]
```

---

## 🛠 Jalankan Lokal (Testing)
```bash
pip install -r requirements.txt
export BOT_TOKEN="TOKEN_KAMU"
python main.py
```
