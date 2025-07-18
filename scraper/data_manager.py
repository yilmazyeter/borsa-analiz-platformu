"""
Veri yönetimi modülü
Verileri kaydetme, yükleme ve takip listesi yönetimi
"""

import json
import os
import sqlite3
from datetime import datetime
import pandas as pd


class DataManager:
    def __init__(self, data_dir="data"):
        self.data_dir = data_dir
        self.db_path = os.path.join(data_dir, "stocks.db")
        self.watchlist_path = os.path.join(data_dir, "watchlist.json")
        
        # Klasörleri oluştur
        os.makedirs(data_dir, exist_ok=True)
        
        # Veritabanını başlat
        self.init_database()
        
    def init_database(self):
        """Veritabanı tablolarını oluşturur"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Hisse verileri tablosu
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS stock_data (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                symbol TEXT NOT NULL,
                current_price REAL,
                daily_change REAL,
                yearly_change REAL,
                volume REAL,
                volume_ratio REAL,
                high_52w REAL,
                low_52w REAL,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Haber verileri tablosu
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS news_data (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                symbol TEXT NOT NULL,
                title TEXT,
                sentiment TEXT,
                sentiment_score REAL,
                source TEXT,
                url TEXT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Analiz sonuçları tablosu
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS analysis_results (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                symbol TEXT NOT NULL,
                analysis_type TEXT,
                result TEXT,
                confidence REAL,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def save_stock_data(self, stock_data):
        """Hisse verilerini veritabanına kaydeder"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO stock_data 
            (symbol, current_price, daily_change, yearly_change, volume, volume_ratio, high_52w, low_52w)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            stock_data['symbol'],
            stock_data['current_price'],
            stock_data['daily_change'],
            stock_data['yearly_change'],
            stock_data['current_volume'],
            stock_data['volume_ratio'],
            stock_data['high_52w'],
            stock_data['low_52w']
        ))
        
        conn.commit()
        conn.close()
    
    def save_news_data(self, news_data):
        """Haber verilerini veritabanına kaydeder"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        for news in news_data.get('news_list', []):
            cursor.execute('''
                INSERT INTO news_data 
                (symbol, title, sentiment, sentiment_score, source, url)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (
                news_data['symbol'],
                news['title'],
                news['sentiment']['sentiment'],
                news['sentiment']['score'],
                news['source'],
                news['url']
            ))
        
        conn.commit()
        conn.close()
    
    def save_analysis_result(self, symbol, analysis_type, result, confidence=0.0):
        """Analiz sonuçlarını veritabanına kaydeder"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO analysis_results 
            (symbol, analysis_type, result, confidence)
            VALUES (?, ?, ?, ?)
        ''', (symbol, analysis_type, result, confidence))
        
        conn.commit()
        conn.close()
    
    def get_watchlist(self):
        """Takip listesini yükler"""
        if os.path.exists(self.watchlist_path):
            with open(self.watchlist_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        return []
    
    def add_to_watchlist(self, symbol, name=""):
        """Takip listesine hisse ekler"""
        watchlist = self.get_watchlist()
        
        # Zaten var mı kontrol et
        if not any(item['symbol'] == symbol for item in watchlist):
            watchlist.append({
                'symbol': symbol,
                'name': name,
                'added_date': datetime.now().isoformat()
            })
            
            with open(self.watchlist_path, 'w', encoding='utf-8') as f:
                json.dump(watchlist, f, ensure_ascii=False, indent=2)
            
            return True
        return False
    
    def remove_from_watchlist(self, symbol):
        """Takip listesinden hisse çıkarır"""
        watchlist = self.get_watchlist()
        watchlist = [item for item in watchlist if item['symbol'] != symbol]
        
        with open(self.watchlist_path, 'w', encoding='utf-8') as f:
            json.dump(watchlist, f, ensure_ascii=False, indent=2)
        
        return True
    
    def get_stock_history(self, symbol, days=30):
        """Hisse geçmiş verilerini getirir"""
        conn = sqlite3.connect(self.db_path)
        
        query = '''
            SELECT * FROM stock_data 
            WHERE symbol = ? 
            ORDER BY timestamp DESC 
            LIMIT ?
        '''
        
        df = pd.read_sql_query(query, conn, params=(symbol, days))
        conn.close()
        
        return df
    
    def get_news_history(self, symbol, days=7):
        """Hisse haber geçmişini getirir"""
        conn = sqlite3.connect(self.db_path)
        
        query = '''
            SELECT * FROM news_data 
            WHERE symbol = ? 
            ORDER BY timestamp DESC 
            LIMIT ?
        '''
        
        df = pd.read_sql_query(query, conn, params=(symbol, days))
        conn.close()
        
        return df
    
    def export_to_csv(self, symbol, output_dir="data/exports"):
        """Hisse verilerini CSV olarak dışa aktarır"""
        os.makedirs(output_dir, exist_ok=True)
        
        # Hisse verileri
        stock_df = self.get_stock_history(symbol, 365)
        stock_file = os.path.join(output_dir, f"{symbol}_stock_data.csv")
        stock_df.to_csv(stock_file, index=False)
        
        # Haber verileri
        news_df = self.get_news_history(symbol, 30)
        news_file = os.path.join(output_dir, f"{symbol}_news_data.csv")
        news_df.to_csv(news_file, index=False)
        
        return {
            'stock_file': stock_file,
            'news_file': news_file
        }
    
    def get_database_stats(self):
        """Veritabanı istatistiklerini getirir"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Tablo satır sayıları
        cursor.execute("SELECT COUNT(*) FROM stock_data")
        stock_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM news_data")
        news_count = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) FROM analysis_results")
        analysis_count = cursor.fetchone()[0]
        
        # Benzersiz hisse sayısı
        cursor.execute("SELECT COUNT(DISTINCT symbol) FROM stock_data")
        unique_stocks = cursor.fetchone()[0]
        
        conn.close()
        
        return {
            'total_stock_records': stock_count,
            'total_news_records': news_count,
            'total_analysis_records': analysis_count,
            'unique_stocks': unique_stocks
        } 