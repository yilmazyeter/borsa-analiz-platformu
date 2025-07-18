@echo off
chcp 65001 >nul
title Borsa Analiz Platformu - Otomatik Başlatma

echo.
echo ======================================================================
echo 🚀 BORSA ANALİZ PLATFORMU - OTOMATİK BAŞLATMA
echo ======================================================================
echo 📅 Başlatma Tarihi: %date% %time%
echo ======================================================================
echo.

:: Python'un yüklü olup olmadığını kontrol et
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python bulunamadı! Lütfen Python'u yükleyin.
    pause
    exit /b 1
)

:: Gerekli dosyaların varlığını kontrol et
if not exist "main.py" (
    echo ❌ main.py dosyası bulunamadı!
    pause
    exit /b 1
)

if not exist "web_app.py" (
    echo ❌ web_app.py dosyası bulunamadı!
    pause
    exit /b 1
)

echo ✅ Sistem kontrolü tamamlandı!
echo.

:menu
echo 📋 BAŞLATMA MENÜSÜ
echo ==========================================
echo 1. 🖥️ Terminal Uygulaması
echo 2. 🌐 Web Uygulaması
echo 3. 🧪 Sistem Testleri
echo 4. 🔄 Her İkisini Başlat
echo 5. 📊 Hızlı Fırsat Analizi
echo 6. 🚀 Python Script ile Başlat
echo 0. ❌ Çıkış
echo ==========================================
echo.

set /p choice="Seçiminizi yapın (0-6): "

if "%choice%"=="0" goto exit
if "%choice%"=="1" goto terminal
if "%choice%"=="2" goto web
if "%choice%"=="3" goto tests
if "%choice%"=="4" goto both
if "%choice%"=="5" goto quick
if "%choice%"=="6" goto python_script

echo ❌ Geçersiz seçim!
echo.
goto menu

:terminal
echo.
echo 🖥️ Terminal Uygulaması Başlatılıyor...
echo --------------------------------------
python main.py
echo.
echo 👋 Terminal uygulaması kapatıldı.
pause
goto menu

:web
echo.
echo 🌐 Web Uygulaması Başlatılıyor...
echo --------------------------------------
echo 📱 Tarayıcınızda http://localhost:8501 adresini açın
echo 🔄 Web uygulamasını durdurmak için Ctrl+C
echo --------------------------------------
streamlit run web_app.py --server.port 8501
echo.
echo 👋 Web uygulaması kapatıldı.
pause
goto menu

:tests
echo.
echo 🧪 Sistem Testleri Çalıştırılıyor...
echo --------------------------------------
python test_opportunity_system.py
echo.
echo ✅ Testler tamamlandı!
pause
goto menu

:both
echo.
echo 🔄 Her İki Uygulama Başlatılıyor...
echo --------------------------------------
echo ⚠️ Bu seçenek deneyseldir. Manuel olarak başlatmanız önerilir.
echo.
echo 1. Önce web uygulamasını başlatın (Seçenek 2)
echo 2. Yeni bir terminal açın
echo 3. Terminal uygulamasını başlatın (Seçenek 1)
echo.
pause
goto menu

:quick
echo.
echo 📊 Hızlı Fırsat Analizi Başlatılıyor...
echo --------------------------------------
python -c "
from analysis.opportunity_analyzer import OpportunityAnalyzer
analyzer = OpportunityAnalyzer()
print('🔍 BIST hisseleri analiz ediliyor...')
bist_opps = analyzer.get_real_time_opportunities(market='bist', min_decline=40)
print('🔍 ABD hisseleri analiz ediliyor...')
us_opps = analyzer.get_real_time_opportunities(market='us', min_decline=40)
all_opps = bist_opps + us_opps
all_opps.sort(key=lambda x: x['opportunity_score'], reverse=True)
print(f'✅ Toplam {len(all_opps)} fırsat bulundu!')
print('🔥 En İyi 5 Fırsat:')
for i, opp in enumerate(all_opps[:5], 1):
    print(f'{i}. {opp[\"symbol\"]}: %{opp[\"total_change\"]:.1f} düşüş, Skor: {opp[\"opportunity_score\"]:.1f}')
"
echo.
pause
goto menu

:python_script
echo.
echo 🚀 Python Script ile Başlatılıyor...
echo --------------------------------------
python start_app.py
echo.
pause
goto menu

:exit
echo.
echo 👋 Görüşürüz!
echo.
pause
exit /b 0 