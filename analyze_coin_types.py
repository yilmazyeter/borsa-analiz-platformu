#!/usr/bin/env python3
"""
Coin Türü Analizi
Bulunan fırsat coinlerinin türünü analiz eder
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from crypto.crypto_analyzer import CryptoAnalyzer

def analyze_coin_types():
    print("🪙 Coin Türü Analizi Başlıyor...")
    
    try:
        # Crypto analyzer'ı başlat
        analyzer = CryptoAnalyzer()
        print("✅ Crypto Analyzer başlatıldı")
        
        # Fırsatları bul
        print("\n🔍 Fırsat coinleri aranıyor...")
        opportunities = analyzer.find_opportunities(min_score=5.0, max_results=20)
        
        if opportunities:
            print(f"✅ {len(opportunities)} fırsat bulundu!")
            print("\n📊 Bulunan Coinler ve Türleri:")
            print("-" * 80)
            
            for i, opp in enumerate(opportunities, 1):
                symbol = opp['symbol']
                price = opp['current_price']
                change_7d = opp['change_7d']
                volume = opp['volume_24h']
                
                # Coin türünü belirle
                coin_type = determine_coin_type(symbol, price, volume)
                
                print(f"{i:2d}. {symbol:12s} | Fiyat: ${price:10.6f} | 7g: {change_7d:6.1f}% | Hacim: ${volume/1000000:6.1f}M | Tür: {coin_type}")
            
            # İstatistikler
            print("\n📈 Coin Türü Dağılımı:")
            coin_types = {}
            for opp in opportunities:
                coin_type = determine_coin_type(opp['symbol'], opp['current_price'], opp['volume_24h'])
                coin_types[coin_type] = coin_types.get(coin_type, 0) + 1
            
            for coin_type, count in coin_types.items():
                percentage = (count / len(opportunities)) * 100
                print(f"   {coin_type}: {count} coin ({percentage:.1f}%)")
            
            # En iyi fırsatlar
            print("\n🔥 En İyi 3 Fırsat:")
            top_opportunities = sorted(opportunities, key=lambda x: x['opportunity_score'], reverse=True)[:3]
            for i, opp in enumerate(top_opportunities, 1):
                coin_type = determine_coin_type(opp['symbol'], opp['current_price'], opp['volume_24h'])
                print(f"   {i}. {opp['symbol']} - Skor: {opp['opportunity_score']:.1f} - Tür: {coin_type}")
        
        else:
            print("❌ Fırsat bulunamadı")
        
        print("\n✅ Coin türü analizi tamamlandı!")
        
    except Exception as e:
        print(f"❌ Analiz sırasında hata: {str(e)}")

def determine_coin_type(symbol, price, volume):
    """Coin'in türünü belirler"""
    
    # Major coins (ana coinler)
    major_coins = ['BTCUSDT', 'ETHUSDT', 'BNBUSDT', 'XRPUSDT', 'ADAUSDT', 'SOLUSDT', 'DOTUSDT', 'LINKUSDT', 'LTCUSDT', 'BCHUSDT']
    
    # Stablecoins (sabit coinler)
    stablecoins = ['USDTUSDT', 'USDCUSDT', 'BUSDUSDT', 'DAIUSDT', 'TUSDUSDT', 'FRAXUSDT']
    
    # Meme coins (meme coinler) - genellikle düşük fiyatlı ve yüksek hacimli
    meme_indicators = ['DOGE', 'SHIB', 'PEPE', 'FLOKI', 'BONK', 'WIF', 'MYRO', 'POPCAT', 'BOOK', 'TURBO']
    
    # DeFi tokens (DeFi tokenleri)
    defi_indicators = ['UNI', 'AAVE', 'COMP', 'MKR', 'SUSHI', 'CRV', 'BAL', 'YFI', 'SNX', '1INCH']
    
    # Gaming tokens (oyun tokenleri)
    gaming_indicators = ['AXS', 'MANA', 'SAND', 'ENJ', 'GALA', 'ILV', 'ALICE', 'HERO', 'TLM', 'ALPHA']
    
    # Layer 1 coins (katman 1 coinler)
    layer1_indicators = ['AVAX', 'MATIC', 'ATOM', 'NEAR', 'FTM', 'ALGO', 'ICP', 'APT', 'SUI', 'SEI']
    
    # Layer 2 coins (katman 2 coinler)
    layer2_indicators = ['ARB', 'OP', 'IMX', 'ZKSYNC', 'STARK', 'POLYGON', 'OPTIMISM']
    
    # AI tokens (yapay zeka tokenleri)
    ai_indicators = ['FET', 'OCEAN', 'AGIX', 'RNDR', 'TAO', 'BITTENSOR', 'AI', 'GPT', 'NEURAL']
    
    # Exchange tokens (borsa tokenleri)
    exchange_indicators = ['BNB', 'OKB', 'HT', 'KCS', 'GT', 'MX', 'BGB', 'CRO', 'FTT']
    
    # Utility tokens (fayda tokenleri)
    utility_indicators = ['LINK', 'CHAINLINK', 'BAT', 'ZRX', 'REP', 'KNC', 'BAND', 'API3']
    
    # Check coin type
    if symbol in major_coins:
        return "Major Coin"
    elif symbol in stablecoins:
        return "Stablecoin"
    elif any(indicator in symbol for indicator in meme_indicators):
        return "Meme Coin"
    elif any(indicator in symbol for indicator in defi_indicators):
        return "DeFi Token"
    elif any(indicator in symbol for indicator in gaming_indicators):
        return "Gaming Token"
    elif any(indicator in symbol for indicator in layer1_indicators):
        return "Layer 1"
    elif any(indicator in symbol for indicator in layer2_indicators):
        return "Layer 2"
    elif any(indicator in symbol for indicator in ai_indicators):
        return "AI Token"
    elif any(indicator in symbol for indicator in exchange_indicators):
        return "Exchange Token"
    elif any(indicator in symbol for indicator in utility_indicators):
        return "Utility Token"
    elif price < 0.01 and volume > 10000000:  # Çok düşük fiyat, yüksek hacim
        return "Altcoin/Meme"
    elif price < 1.0:
        return "Altcoin"
    elif volume < 1000000:  # Düşük hacim
        return "Micro Cap"
    else:
        return "Altcoin"

if __name__ == "__main__":
    analyze_coin_types() 