#!/bin/bash

# Borsa Analiz Platformu - Otomatik Başlatma Scripti

# Renk kodları
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Banner yazdır
print_banner() {
    echo -e "${BLUE}======================================================================${NC}"
    echo -e "${BLUE}🚀 BORSA ANALİZ PLATFORMU - OTOMATİK BAŞLATMA${NC}"
    echo -e "${BLUE}======================================================================${NC}"
    echo -e "${BLUE}📅 Başlatma Tarihi: $(date '+%Y-%m-%d %H:%M:%S')${NC}"
    echo -e "${BLUE}======================================================================${NC}"
    echo
}

# Bağımlılıkları kontrol et
check_dependencies() {
    echo -e "${YELLOW}🔍 Gerekli kütüphaneler kontrol ediliyor...${NC}"
    
    # Python kontrolü
    if ! command -v python3 &> /dev/null; then
        echo -e "${RED}❌ Python3 bulunamadı! Lütfen Python'u yükleyin.${NC}"
        return 1
    fi
    
    # Gerekli dosyaları kontrol et
    if [ ! -f "main.py" ]; then
        echo -e "${RED}❌ main.py dosyası bulunamadı!${NC}"
        return 1
    fi
    
    if [ ! -f "web_app.py" ]; then
        echo -e "${RED}❌ web_app.py dosyası bulunamadı!${NC}"
        return 1
    fi
    
    echo -e "${GREEN}✅ Sistem kontrolü tamamlandı!${NC}"
    return 0
}

# Terminal uygulamasını başlat
start_terminal_app() {
    echo
    echo -e "${BLUE}🖥️ Terminal Uygulaması Başlatılıyor...${NC}"
    echo -e "${BLUE}--------------------------------------${NC}"
    
    python3 main.py
    
    echo
    echo -e "${YELLOW}👋 Terminal uygulaması kapatıldı.${NC}"
    read -p "Devam etmek için Enter'a basın..."
}

# Web uygulamasını başlat
start_web_app() {
    echo
    echo -e "${BLUE}🌐 Web Uygulaması Başlatılıyor...${NC}"
    echo -e "${BLUE}--------------------------------------${NC}"
    echo -e "${GREEN}📱 Tarayıcınızda http://localhost:8501 adresini açın${NC}"
    echo -e "${YELLOW}🔄 Web uygulamasını durdurmak için Ctrl+C${NC}"
    echo -e "${BLUE}--------------------------------------${NC}"
    
    streamlit run web_app.py --server.port 8501
    
    echo
    echo -e "${YELLOW}👋 Web uygulaması kapatıldı.${NC}"
    read -p "Devam etmek için Enter'a basın..."
}

# Testleri çalıştır
run_tests() {
    echo
    echo -e "${BLUE}🧪 Sistem Testleri Çalıştırılıyor...${NC}"
    echo -e "${BLUE}--------------------------------------${NC}"
    
    python3 test_opportunity_system.py
    
    echo
    echo -e "${GREEN}✅ Testler tamamlandı!${NC}"
    read -p "Devam etmek için Enter'a basın..."
}

# Hızlı fırsat analizi
quick_analysis() {
    echo
    echo -e "${BLUE}📊 Hızlı Fırsat Analizi Başlatılıyor...${NC}"
    echo -e "${BLUE}--------------------------------------${NC}"
    
    python3 -c "
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
    
    echo
    read -p "Devam etmek için Enter'a basın..."
}

# Her ikisini başlat
start_both() {
    echo
    echo -e "${BLUE}🔄 Her İki Uygulama Başlatılıyor...${NC}"
    echo -e "${BLUE}--------------------------------------${NC}"
    echo -e "${YELLOW}⚠️ Bu seçenek deneyseldir. Manuel olarak başlatmanız önerilir.${NC}"
    echo
    echo -e "${GREEN}1. Önce web uygulamasını başlatın (Seçenek 2)${NC}"
    echo -e "${GREEN}2. Yeni bir terminal açın${NC}"
    echo -e "${GREEN}3. Terminal uygulamasını başlatın (Seçenek 1)${NC}"
    echo
    read -p "Devam etmek için Enter'a basın..."
}

# Menüyü göster
show_menu() {
    echo
    echo -e "${BLUE}📋 BAŞLATMA MENÜSÜ${NC}"
    echo -e "${BLUE}==========================================${NC}"
    echo -e "${GREEN}1. 🖥️ Terminal Uygulaması${NC}"
    echo -e "${GREEN}2. 🌐 Web Uygulaması${NC}"
    echo -e "${GREEN}3. 🧪 Sistem Testleri${NC}"
    echo -e "${GREEN}4. 🔄 Her İkisini Başlat${NC}"
    echo -e "${GREEN}5. 📊 Hızlı Fırsat Analizi${NC}"
    echo -e "${GREEN}6. 🚀 Python Script ile Başlat${NC}"
    echo -e "${RED}0. ❌ Çıkış${NC}"
    echo -e "${BLUE}==========================================${NC}"
    echo
}

# Ana fonksiyon
main() {
    print_banner
    
    # Bağımlılıkları kontrol et
    if ! check_dependencies; then
        echo -e "${RED}❌ Sistem kontrolü başarısız!${NC}"
        exit 1
    fi
    
    while true; do
        show_menu
        
        read -p "Seçiminizi yapın (0-6): " choice
        
        case $choice in
            0)
                echo
                echo -e "${YELLOW}👋 Görüşürüz!${NC}"
                echo
                exit 0
                ;;
            1)
                start_terminal_app
                ;;
            2)
                start_web_app
                ;;
            3)
                run_tests
                ;;
            4)
                start_both
                ;;
            5)
                quick_analysis
                ;;
            6)
                echo
                echo -e "${BLUE}🚀 Python Script ile Başlatılıyor...${NC}"
                echo -e "${BLUE}--------------------------------------${NC}"
                python3 start_app.py
                echo
                read -p "Devam etmek için Enter'a basın..."
                ;;
            *)
                echo -e "${RED}❌ Geçersiz seçim!${NC}"
                echo
                ;;
        esac
    done
}

# Script'i çalıştırılabilir yap
chmod +x "$0"

# Ana fonksiyonu çağır
main 