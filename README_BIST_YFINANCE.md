# BIST Hisse Senedi yfinance Entegrasyonu

Bu modül, BIST (Borsa İstanbul) hisseleri için yfinance API entegrasyonu sağlar. Rate limiting sorunlarına karşı korumalı ve mock data fallback sistemi içerir.

## 🚀 Özellikler

- ✅ BIST hisseleri için yfinance API entegrasyonu
- ✅ Rate limiting yönetimi ve yeniden deneme mekanizması
- ✅ Mock data fallback sistemi
- ✅ CSV kaydetme/yükleme özellikleri
- ✅ Çoklu hisse verisi çekme
- ✅ Türkçe sütun isimleri
- ✅ Detaylı hata yönetimi

## 📦 Kurulum

### Gereksinimler

```bash
pip install yfinance pandas requests matplotlib
```

### Mevcut requirements.txt'ye ekleme

```bash
pip install -r requirements.txt
```

## 🔧 Kullanım

### Temel Kullanım

```python
from bist_yfinance_integration import BISTYFinanceIntegration
from datetime import datetime, timedelta

# BIST entegrasyon örneği oluştur
bist = BISTYFinanceIntegration()

# Tarih aralığı belirle
end_date = datetime.now().strftime('%Y-%m-%d')
start_date = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')

# Hisse verisi çek
symbol = "ASELS.IS"
df = bist.get_bist_stock_data(symbol, start_date, end_date)

if df is not None:
    print(f"Veri alındı: {len(df)} kayıt")
    print(f"Son kapanış: {df['Kapanış'].iloc[-1]:.2f} TL")
```

### Hisse Bilgisi Alma

```python
# Hisse detay bilgisi al
info = bist.get_bist_stock_info("GARAN.IS")

if info:
    print(f"Şirket: {info['name']}")
    print(f"Güncel fiyat: {info['current_price']:.2f} TL")
    print(f"Günlük değişim: {info['daily_change_percent']:.2f}%")
    print(f"Sektör: {info['sector']}")
```

### Çoklu Hisse Verisi

```python
# Birden fazla hisse için veri çek
symbols = ["ASELS.IS", "GARAN.IS", "THYAO.IS"]
results = bist.get_multiple_bist_stocks(symbols, start_date, end_date)

for symbol, df in results.items():
    if df is not None:
        print(f"{symbol}: {len(df)} kayıt")
```

### CSV İşlemleri

```python
# Veriyi CSV'ye kaydet
filename = "data/asels_data.csv"
bist.save_data_to_csv(df, filename)

# CSV'den veri yükle
loaded_df = bist.load_data_to_csv(filename)
```

### Mock Data Kullanımı

```python
# Rate limiting durumunda mock data oluştur
mock_df = bist.get_mock_bist_data("ASELS.IS", start_date, end_date)
```

## 📊 Veri Formatı

### Hisse Verisi (DataFrame)

| Sütun | Açıklama | Örnek |
|-------|----------|-------|
| Tarih | İşlem tarihi | 2025-07-18 |
| Açılış | Açılış fiyatı | 150.25 |
| Yüksek | Günlük en yüksek | 155.80 |
| Düşük | Günlük en düşük | 148.90 |
| Kapanış | Kapanış fiyatı | 152.30 |
| Hacim | İşlem hacmi | 1,250,000 |

### Hisse Bilgisi (Dictionary)

```python
{
    'symbol': 'ASELS.IS',
    'name': 'Aselsan Elektronik Sanayi ve Ticaret A.Ş.',
    'sector': 'Teknoloji',
    'industry': 'Savunma',
    'current_price': 152.30,
    'daily_change_percent': 1.35,
    'market_cap': 15000000000,
    'pe_ratio': 15.2,
    'currency': 'TL',
    'exchange': 'IST'
}
```

## 🔍 Desteklenen Hisse Kodları

### Popüler BIST Hisseleri

- **ASELS.IS** - Aselsan
- **GARAN.IS** - Garanti Bankası
- **THYAO.IS** - Türk Hava Yolları
- **AKBNK.IS** - Akbank
- **EREGL.IS** - Ereğli Demir ve Çelik
- **KCHOL.IS** - Koç Holding
- **SAHOL.IS** - Sabancı Holding
- **SISE.IS** - Şişe Cam
- **TUPRS.IS** - Tüpraş
- **BIMAS.IS** - BİM

## ⚙️ Konfigürasyon

### Rate Limiting Ayarları

```python
bist = BISTYFinanceIntegration()
bist.rate_limit_delay = 3.0  # Bekleme süresi (saniye)
bist.max_retries = 5         # Maksimum deneme sayısı
```

### Önbellek Yönetimi

```python
# Önbelleği temizle
bist.cache.clear()

# Önbellek boyutunu kontrol et
print(f"Önbellek boyutu: {len(bist.cache)}")
```

## 🛠️ Hata Yönetimi

### Yaygın Hatalar ve Çözümler

1. **429 Too Many Requests**
   - Rate limiting nedeniyle oluşur
   - Sistem otomatik olarak bekler ve yeniden dener
   - Mock data fallback sistemi devreye girer

2. **Veri Bulunamadı**
   - Hisse kodu yanlış olabilir
   - Tarih aralığı geçersiz olabilir
   - Mock data kullanılır

3. **Bağlantı Hatası**
   - İnternet bağlantısını kontrol edin
   - Proxy ayarlarını kontrol edin

## 📈 Veri Analizi Örnekleri

### Temel İstatistikler

```python
# Günlük değişim hesapla
df['Günlük_Değişim'] = df['Kapanış'].pct_change() * 100

# Volatilite hesapla
volatility = df['Günlük_Değişim'].std()

# Trend analizi
last_5_days = df.tail(5)
trend = "Yükseliş" if last_5_days['Kapanış'].iloc[-1] > last_5_days['Kapanış'].iloc[0] else "Düşüş"
```

### Görselleştirme

```python
import matplotlib.pyplot as plt

# Fiyat grafiği
plt.plot(df['Tarih'], df['Kapanış'])
plt.title('Hisse Fiyat Grafiği')
plt.xlabel('Tarih')
plt.ylabel('Fiyat (TL)')
plt.xticks(rotation=45)
plt.show()
```

## 🧪 Test

### Test Dosyaları

1. **test_yfinance_bist.py** - Temel entegrasyon testi
2. **test_bist_symbols.py** - Sembol formatları testi
3. **demo_bist_yfinance.py** - Kapsamlı demo
4. **demo_mock_data.py** - Mock data testi

### Test Çalıştırma

```bash
# Temel test
python test_yfinance_bist.py

# Mock data testi
python demo_mock_data.py

# Kapsamlı demo
python demo_bist_yfinance.py
```

## 📁 Dosya Yapısı

```
borsa/
├── bist_yfinance_integration.py    # Ana entegrasyon modülü
├── test_yfinance_bist.py          # Test dosyası
├── test_bist_symbols.py           # Sembol testi
├── demo_bist_yfinance.py          # Demo dosyası
├── demo_mock_data.py              # Mock data demo
├── data/                          # Veri dosyaları
│   ├── ASELS_mock_data.csv
│   ├── GARAN_mock_data.csv
│   └── THYAO_mock_data.csv
└── README_BIST_YFINANCE.md        # Bu dosya
```

## 🔄 Güncellemeler

### v1.0.0 (2025-07-18)
- ✅ İlk sürüm
- ✅ yfinance entegrasyonu
- ✅ Rate limiting yönetimi
- ✅ Mock data sistemi
- ✅ CSV işlemleri
- ✅ Çoklu hisse desteği

## 🤝 Katkıda Bulunma

1. Fork yapın
2. Feature branch oluşturun (`git checkout -b feature/amazing-feature`)
3. Commit yapın (`git commit -m 'Add amazing feature'`)
4. Push yapın (`git push origin feature/amazing-feature`)
5. Pull Request oluşturun

## 📄 Lisans

Bu proje MIT lisansı altında lisanslanmıştır.

## 📞 Destek

Sorularınız için:
- GitHub Issues kullanın
- Proje dokümantasyonunu inceleyin
- Test dosyalarını çalıştırın

## ⚠️ Uyarılar

- yfinance API'si rate limiting uygular
- Gerçek veri alınamadığında mock data kullanılır
- Hisse kodları doğru formatta olmalıdır (.IS uzantısı)
- Tarih aralıkları geçerli olmalıdır

---

**Not:** Bu modül eğitim ve geliştirme amaçlıdır. Ticari kullanım için lütfen gerekli lisansları kontrol edin. 