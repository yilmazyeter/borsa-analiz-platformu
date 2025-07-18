# 📈 Hisse Takip ve Analiz Platformu

Bu proje, BIST ve ABD hisselerini analiz etmek, fırsatları değerlendirmek ve sanal trading yapmak için geliştirilmiş kapsamlı bir platformdur.

## 🚀 Canlı Demo

**Streamlit Cloud'da Canlı Demo:** [https://borsa-analiz.streamlit.app](https://borsa-analiz.streamlit.app)

## 👨‍💻 Geliştirici

**Geliştirici:** Gökhan İşcanlı

## 🛠️ Teknolojiler

- 🐍 Python
- 📊 Streamlit
- 🤖 AI/ML Modelleri
- 📈 Plotly Grafikleri
- 💾 SQLite Veritabanı
- 📰 Haber Analizi
- 🔔 Alarm Sistemi

## 🚀 Yeni Özellikler

- ✅ **Anlık Fırsat Analizi**: Son 1 yılda düşüş geçmiş ve yükselme potansiyeli olan BIST ve ABD hisselerini anlık veri ile analiz
- ✅ **Hayali Alım-Satım Sistemi**: Gökhan ve Yılmaz kullanıcıları ile 300.000 TL sanal para ile gerçek hisse alım-satımı
- ✅ **7 Günlük Performans Takibi**: Alınan hisselerin 7 günlük kar/zarar değerlendirmesi
- ✅ **Takip Listesi Entegrasyonu**: Fırsat analizinden takip listesine otomatik ekleme
- ✅ **Web Arayüzü**: Streamlit ile modern ve kullanıcı dostu arayüz
- ✅ **Otomatik Başlatma Scriptleri**: Windows, Linux/Mac için otomatik başlatma

## 📊 Özellikler

- ✅ Son 1 yılda %40-80 değer kaybetmiş hisseleri tespit etme
- ✅ Otomatik veri çekme (fiyat, hacim, haberler)
- ✅ Haber sentiment analizi (AI destekli)
- ✅ Trend ve risk analizi
- ✅ Detaylı hisse inceleme raporları
- ✅ Grafik görselleştirme
- ✅ PDF rapor üretimi
- ✅ Bildirim sistemi (Telegram)

## 🛠️ Kurulum

1. Gerekli kütüphaneleri yükleyin:
```bash
pip install -r requirements.txt
```

2. `.env` dosyası oluşturun:
```
OPENAI_API_KEY=your_openai_api_key
TELEGRAM_BOT_TOKEN=your_telegram_bot_token
TELEGRAM_CHAT_ID=your_chat_id
```

## 🚀 Otomatik Başlatma

### Windows Kullanıcıları:
```bash
# Batch dosyasını çift tıklayın veya:
start_app.bat
```

### Linux/Mac Kullanıcıları:
```bash
# Shell script'i çalıştırın:
./start_app.sh
```

### Python Script (Tüm Platformlar):
```bash
python start_app.py
```

### Manuel Başlatma:
```bash
# Terminal uygulaması
python main.py

# Web uygulaması
streamlit run web_app.py
```

## 🎯 Kullanım

### 1. Anlık Fırsat Analizi
```bash
python main.py
# Menüden "1. 🔍 Anlık Fırsat Analizi" seçin
```

### 2. Hayali Alım-Satım
```bash
python main.py
# Menüden "2. 💰 Hayali Alım-Satım Demo" seçin
```

### 3. Web Arayüzü
```bash
python main.py
# Menüden "7. 🚀 Web Uygulamasını Başlat" seçin
# veya doğrudan:
streamlit run web_app.py
```

## 📁 Proje Yapısı

```
borsa/
├── analysis/           # Analiz modülleri
│   ├── opportunity_analyzer.py  # Fırsat analizi
│   ├── risk_analyzer.py         # Risk analizi
│   ├── technical_analyzer.py    # Teknik analiz
│   └── trend_analyzer.py        # Trend analizi
├── data/              # Veri yönetimi
│   ├── data_manager.py         # Veri yöneticisi
│   └── watchlist.json          # Takip listesi
├── alerts/            # Alarm sistemi
│   ├── alert_manager.py        # Alarm yöneticisi
│   └── notification_system.py  # Bildirim sistemi
├── start_app.py       # Python başlatma scripti
├── start_app.bat      # Windows başlatma scripti
├── start_app.sh       # Linux/Mac başlatma scripti
├── web_app.py         # Web arayüzü
├── main.py            # Ana uygulama
└── requirements.txt   # Gereksinimler
```

## 🔍 Fırsat Analizi Sistemi

### Özellikler:
- **BIST ve ABD Hisseleri**: Her iki piyasadan anlık veri çekme
- **Düşüş Kriterleri**: Son 1 yılda %40-80 değer kaybı
- **Fırsat Skoru**: Çoklu faktör analizi ile 0-100 arası skor
- **Toparlanma Analizi**: Son 30 günlük toparlanma trendi
- **Hacim Analizi**: Hacim artışı ve trend analizi

### Fırsat Faktörleri:
- 📉 Büyük değer kaybı geçmişi
- 📈 Toparlanma başlangıcı
- 📊 Yüksek hacim artışı
- 💰 Uygun fiyat seviyesi
- 📈 Teknik göstergeler

## 💰 Hayali Alım-Satım Sistemi

### Kullanıcılar:
- **Gökhan**: 300.000 TL başlangıç bakiyesi
- **Yılmaz**: 300.000 TL başlangıç bakiyesi

### Özellikler:
- 📈 Gerçek hisse alım-satımı
- 📊 Portföy yönetimi
- 📋 İşlem geçmişi
- 📈 7 günlük performans takibi
- 💰 Kar/zarar hesaplama

### Performans Takibi:
- 📅 Alım tarihinden itibaren 7 gün takip
- 📊 Günlük kar/zarar hesaplama
- 📈 Yüzdelik getiri analizi
- 🎯 Otomatik değerlendirme

## 🌐 Web Arayüzü

### Modüller:
1. **🏠 Ana Sayfa**: Genel özet ve popüler hisseler
2. **📊 Hisse Analizi**: Tek hisse detay analizi
3. **🎯 Fırsat Analizi**: Anlık fırsat analizi ve takibe alma
4. **💰 Hayali Alım-Satım**: Gökhan/Yılmaz ile işlem yapma
5. **📰 Haber Analizi**: Hisse haberleri ve sentiment
6. **💼 Portföy**: Portföy yönetimi ve takip
7. **🔔 Alarmlar**: Fiyat alarmları
8. **🤖 AI Asistan**: Yapay zeka destekli öneriler

## 🧪 Test

Sistem testlerini çalıştırmak için:
```bash
python test_opportunity_system.py
```

## 📈 Örnek Kullanım

### 1. Fırsat Analizi
```python
from analysis.opportunity_analyzer import OpportunityAnalyzer

analyzer = OpportunityAnalyzer()
opportunities = analyzer.get_real_time_opportunities(market='both', min_decline=40)

for opp in opportunities[:5]:
    print(f"{opp['symbol']}: %{opp['total_change']:.1f} düşüş, Skor: {opp['opportunity_score']:.1f}")
```

### 2. Hayali Alım-Satım
```python
from data.data_manager import DataManager

data_manager = DataManager()

# Alım işlemi
success, message = data_manager.buy_stock("gokhan", "THYAO.IS", 100, 25.50)

# Performans takibi
performance = data_manager.get_performance_tracking("gokhan")
```

## 🔧 Geliştirme

### Yeni Özellik Ekleme:
1. İlgili modülü güncelleyin
2. Test dosyası oluşturun
3. Web arayüzünü güncelleyin
4. README'yi güncelleyin

### Veritabanı Şeması:
- `virtual_users`: Kullanıcı bilgileri
- `virtual_portfolio`: Portföy verileri
- `virtual_transactions`: İşlem geçmişi
- `virtual_performance`: Performans takibi
- `watchlist`: Takip listesi

## 📞 Destek

Sorularınız için:
- 📧 Email: support@example.com
- 📱 Telegram: @borsa_support
- 🌐 Web: https://example.com/support

## 📄 Lisans

Bu proje MIT lisansı altında lisanslanmıştır.

---

**🚀 Projeyi başlatmak için:**

### Windows:
```bash
start_app.bat
```

### Linux/Mac:
```bash
./start_app.sh
```

### Python (Tüm Platformlar):
```bash
python start_app.py
```

### Manuel:
```bash
python main.py
``` 