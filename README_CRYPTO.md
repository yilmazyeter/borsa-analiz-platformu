# 🪙 Crypto Analizi Modülü

Bu modül, USDT üzerindeki kripto para birimlerinin anlık analizini yapar ve fırsat tespiti gerçekleştirir.

## 🚀 Özellikler

### 📊 **Anlık Veri Analizi**
- **Binance API v3** entegrasyonu
- **1 saatlik, 4 saatlik, günlük** mum verileri
- **7 günlük geçmiş** veri analizi
- **24 saatlik hacim** takibi

### 🎯 **Fırsat Tespiti**
- **Düşüş gösteren coinlerin** tespiti
- **Kısa vadeli artış potansiyeli** analizi
- **Fırsat skorlaması** sistemi
- **Otomatik öneri** mekanizması

### 📈 **Teknik Analiz**
- **RSI (Relative Strength Index)**
- **SMA (Simple Moving Average)**
- **EMA (Exponential Moving Average)**
- **MACD (Moving Average Convergence Divergence)**
- **Bollinger Bands**
- **Stochastic RSI**

### 🔔 **Takip Sistemi**
- **Otomatik takip listesi** ekleme
- **Fırsat coinlerinin** izlenmesi
- **Performans takibi**

## 🛠️ Kurulum

### Gereksinimler
```bash
pip install -r requirements.txt
```

### Gerekli Kütüphaneler
- `requests` - API istekleri için
- `pandas` - Veri işleme
- `numpy` - Matematiksel hesaplamalar
- `plotly` - Grafik oluşturma

## 📖 Kullanım

### 1. Crypto Analyzer Başlatma
```python
from crypto.crypto_analyzer import CryptoAnalyzer

analyzer = CryptoAnalyzer()
```

### 2. USDT Çiftlerini Alma
```python
usdt_pairs = analyzer.get_all_usdt_pairs()
print(f"Toplam {len(usdt_pairs)} USDT çifti bulundu")
```

### 3. Coin Verisi Alma
```python
btc_data = analyzer.get_coin_data("BTCUSDT")
print(f"Güncel fiyat: ${btc_data['current_price']:.2f}")
print(f"24h değişim: {btc_data['change_24h']:.2f}%")
```

### 4. Fırsat Analizi
```python
opportunities = analyzer.find_opportunities(min_score=10.0, max_results=20)
for opp in opportunities:
    print(f"{opp['symbol']}: Skor={opp['opportunity_score']:.1f}")
```

### 5. Teknik Göstergeler
```python
indicators = analyzer.calculate_technical_indicators(coin_data['data'])
print(f"RSI: {indicators['rsi']:.1f}")
print(f"SMA 20: {indicators['sma_20']:.2f}")
```

## 🎯 Fırsat Tespit Algoritması

### Skorlama Sistemi
1. **Hacim Kontrolü** - Minimum 1M USDT hacim
2. **Düşüş Analizi** - %5'ten fazla düşüş
3. **Toparlanma Tespiti** - Son 24 saatte artış
4. **Aşırı Düşüş** - %20'den fazla düşüş bonusu
5. **Hacim Artışı** - %50'den fazla hacim artışı
6. **Teknik Göstergeler** - RSI < 30 (aşırı satım)

### Fırsat Tipleri
- **Düşüş Fırsatı** - Uzun vadeli düşüş sonrası
- **Toparlanma Fırsatı** - Düşüş sonrası toparlanma
- **Aşırı Düşüş Fırsatı** - Büyük düşüş sonrası
- **Hacim Artışı** - Hacim patlaması ile birlikte

## 📊 Web Arayüzü

### Ana Sayfalar
1. **🚀 Fırsat Analizi** - Otomatik fırsat tespiti
2. **📊 Coin Detayları** - Detaylı coin analizi
3. **📈 Grafik Analizi** - Teknik grafikler
4. **⚙️ Ayarlar** - Analiz parametreleri

### Özellikler
- **Gerçek zamanlı** veri güncelleme
- **İnteraktif grafikler** (Plotly)
- **Otomatik takip** listesi ekleme
- **Filtreleme** seçenekleri
- **Performans** takibi

## 🔧 Konfigürasyon

### Analiz Parametreleri
```python
analyzer.min_volume_usdt = 1000000  # Minimum hacim
analyzer.min_price_change = 2.0     # Minimum değişim
analyzer.opportunity_threshold = 5.0 # Fırsat eşiği
analyzer.cache_duration = 60        # Cache süresi
```

### API Limitleri
- **Rate Limiting** - Her 10 istekte 1 saniye bekleme
- **Cache Sistemi** - 60 saniye cache süresi
- **Hata Yönetimi** - Otomatik yeniden deneme

## 🧪 Test

### Test Dosyası Çalıştırma
```bash
python test_crypto_analyzer.py
```

### Test Edilen Özellikler
- ✅ USDT çiftleri alma
- ✅ Coin verisi çekme
- ✅ Fırsat analizi
- ✅ Teknik göstergeler
- ✅ Grafik verisi

## 📈 Performans

### Optimizasyonlar
- **Cache sistemi** - API çağrılarını azaltır
- **Rate limiting** - API limitlerini aşmaz
- **Verimli algoritmalar** - Hızlı analiz
- **Paralel işleme** - Çoklu coin analizi

### Sınırlamalar
- **API limitleri** - Binance API kısıtlamaları
- **Veri kalitesi** - Anlık veri bağımlılığı
- **Piyasa volatilitesi** - Hızlı değişimler

## 🔮 Gelecek Özellikler

### Planlanan Geliştirmeler
- [ ] **Daha fazla borsa** entegrasyonu
- [ ] **AI destekli** fiyat tahmini
- [ ] **Portföy optimizasyonu**
- [ ] **Otomatik trading** sinyalleri
- [ ] **Sosyal sentiment** analizi
- [ ] **Haber analizi** entegrasyonu

### Teknik İyileştirmeler
- [ ] **WebSocket** gerçek zamanlı veri
- [ ] **Daha fazla teknik gösterge**
- [ ] **Gelişmiş grafik** özellikleri
- [ ] **Backtesting** sistemi
- [ ] **Risk yönetimi** araçları

## 📞 Destek

### İletişim
- **Geliştirici:** Gökhan İşcanlı
- **Email:** gokhan.iscanli@example.com
- **GitHub:** github.com/gokhaniscanli

### Katkıda Bulunma
1. Fork yapın
2. Feature branch oluşturun
3. Değişikliklerinizi commit edin
4. Pull request gönderin

## ⚠️ Uyarılar

### Risk Uyarısı
- Bu araç **sadece analiz** amaçlıdır
- **Yatırım tavsiyesi** değildir
- **Kendi riskinizle** kullanın
- **Piyasa araştırması** yapın

### Teknik Uyarılar
- API limitlerine dikkat edin
- Veri kalitesini kontrol edin
- Sistem performansını izleyin
- Hata loglarını takip edin

---

**🪙 Crypto Analizi Modülü** - Akıllı kripto para analizi ve fırsat tespiti 