# Streamlit Cloud Deployment Guide

## Streamlit Cloud'a Deploy Etme

### 1. GitHub'a Yükleme

1. **GitHub Repository Oluşturun:**
   ```bash
   git init
   git add .
   git commit -m "Initial commit"
   git branch -M main
   git remote add origin https://github.com/KULLANICI_ADINIZ/REPO_ADINIZ.git
   git push -u origin main
   ```

2. **Gerekli Dosyalar:**
   - `web_app_backup.py` (ana uygulama)
   - `requirements.txt` (bağımlılıklar)
   - `.streamlit/config.toml` (konfigürasyon)

### 2. Streamlit Cloud'a Deploy

1. **Streamlit Cloud'a Gidin:**
   - https://share.streamlit.io/
   - GitHub hesabınızla giriş yapın

2. **Yeni Uygulama Oluşturun:**
   - "New app" butonuna tıklayın
   - Repository: `KULLANICI_ADINIZ/REPO_ADINIZ`
   - Branch: `main`
   - Main file path: `web_app_backup.py`

3. **Deploy Edin:**
   - "Deploy!" butonuna tıklayın
   - Uygulama otomatik olarak build edilecek

### 3. Alternatif Platformlar

#### Heroku (Ücretli)
```bash
# Procfile oluşturun
echo "web: streamlit run web_app_backup.py --server.port=\$PORT --server.address=0.0.0.0" > Procfile

# Heroku CLI ile deploy
heroku create YOUR_APP_NAME
git push heroku main
```

#### Railway (Ücretsiz/Ücretli)
1. Railway.app'e gidin
2. GitHub repository'nizi bağlayın
3. Otomatik deploy

#### Render (Ücretsiz/Ücretli)
1. Render.com'a gidin
2. "New Web Service" seçin
3. GitHub repository'nizi bağlayın
4. Build command: `pip install -r requirements.txt`
5. Start command: `streamlit run web_app_backup.py --server.port=\$PORT --server.address=0.0.0.0`

### 4. Sorun Giderme

#### Import Hataları
- Tüm modüller ana dosyaya gömülmüştür
- `requirements.txt` güncellenmiştir
- Streamlit Cloud'da çalışacak şekilde düzenlenmiştir

#### Memory Limitleri
- Streamlit Cloud: 1GB RAM
- Büyük veri işlemleri için optimize edilmiştir
- Cache sistemi kullanılmıştır

#### Timeout Sorunları
- API çağrıları timeout ile korunmuştur
- Hata yakalama mekanizmaları eklenmiştir

### 5. Özellikler

✅ **Çalışan Özellikler:**
- Kripto para analizi
- Virtual trading
- Portfolio yönetimi
- Watchlist
- Transaction history
- Real-time data
- Whale analysis
- 1h profit analysis

✅ **Deployment Hazır:**
- Import hataları düzeltildi
- Modüller gömüldü
- Requirements güncellendi
- Config dosyası eklendi

### 6. URL Yapısı

Deploy sonrası URL:
```
https://KULLANICI_ADINIZ-REPO_ADINIZ-APP_ID.streamlit.app
```

### 7. Güncelleme

Kod güncellemeleri için:
```bash
git add .
git commit -m "Update"
git push origin main
```

Streamlit Cloud otomatik olarak yeniden deploy edecektir.

### 8. Monitoring

- Streamlit Cloud dashboard'unda logları görüntüleyin
- Hata mesajlarını kontrol edin
- Performance metriklerini izleyin

### 9. Güvenlik

- API anahtarları environment variables olarak saklayın
- Sensitive data'yı kod içinde tutmayın
- HTTPS kullanın (Streamlit Cloud otomatik)

### 10. Performance

- Cache kullanımı optimize edildi
- API çağrıları minimize edildi
- Memory kullanımı optimize edildi
- Loading states eklendi 