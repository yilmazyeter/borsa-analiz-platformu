"""
Veri yönetimi modülü
Verileri kaydetme, yükleme ve takip listesi yönetimi
"""

import json
import os
import sqlite3
from datetime import datetime, timedelta
import pandas as pd
import warnings
warnings.filterwarnings('ignore')

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
                analysis_type TEXT NOT NULL,
                result TEXT,
                confidence REAL DEFAULT 0.0,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Sanal kullanıcılar tablosu
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS virtual_users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                balance REAL DEFAULT 300000.0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Sanal portföy tablosu
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS virtual_portfolio (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                symbol TEXT NOT NULL,
                shares INTEGER NOT NULL,
                avg_price REAL NOT NULL,
                purchase_date TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES virtual_users (id)
            )
        ''')
        
        # Sanal işlem geçmişi tablosu
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS virtual_transactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                symbol TEXT NOT NULL,
                transaction_type TEXT NOT NULL,
                shares INTEGER NOT NULL,
                price REAL NOT NULL,
                total_amount REAL NOT NULL,
                transaction_date TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES virtual_users (id)
            )
        ''')
        
        # Sanal performans takibi tablosu (7 günlük)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS virtual_performance (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                symbol TEXT NOT NULL,
                initial_investment REAL NOT NULL,
                current_value REAL NOT NULL,
                profit_loss REAL NOT NULL,
                profit_loss_percent REAL NOT NULL,
                tracking_start_date TEXT NOT NULL,
                tracking_end_date TEXT,
                status TEXT DEFAULT 'active',
                days_held INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES virtual_users (id)
            )
            ''')
        
        conn.commit()
        conn.close()
        
        # Varsayılan kullanıcıları oluştur
        self.create_default_users()
    
    def create_default_users(self):
        """Varsayılan sanal kullanıcıları oluştur"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Kullanıcıları kontrol et ve yoksa ekle
            users = [
                ('gokhan', 300000.0),
                ('yilmaz', 300000.0)
            ]
            
            for username, balance in users:
                cursor.execute('''
                    INSERT OR IGNORE INTO virtual_users (username, balance)
                    VALUES (?, ?)
                ''', (username, balance))
            
            conn.commit()
    
    def save_stock_data(self, symbol, data):
        """Hisse verilerini kaydet"""
        if not data or 'historical_data' not in data:
            return False
        
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            for record in data['historical_data']:
                cursor.execute('''
                    INSERT OR REPLACE INTO stock_data 
                    (symbol, date, open, high, low, close, volume)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', (
                    symbol,
                    record['Date'],
                    record.get('Open'),
                    record.get('High'),
                    record.get('Low'),
                    record.get('Close'),
                    record.get('Volume', 0)
                ))
            
            conn.commit()
            return True
    
    def get_stock_data(self, symbol, days=365):
        """Hisse verilerini getir"""
        with sqlite3.connect(self.db_path) as conn:
            query = '''
                SELECT date, open, high, low, close, volume
                FROM stock_data 
                WHERE symbol = ?
                ORDER BY date DESC
                LIMIT ?
            '''
            
            df = pd.read_sql_query(query, conn, params=(symbol, days))
            return df.to_dict('records') if not df.empty else []
    
    def save_analysis_result(self, symbol, analysis_type, results):
        """Analiz sonuçlarını kaydet"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO analysis_results (symbol, analysis_date, analysis_type, results)
                VALUES (?, ?, ?, ?)
            ''', (symbol, datetime.now().strftime('%Y-%m-%d'), analysis_type, json.dumps(results)))
            conn.commit()
    
    def get_analysis_results(self, symbol, analysis_type=None):
        """Analiz sonuçlarını getir"""
        with sqlite3.connect(self.db_path) as conn:
            if analysis_type:
                query = '''
                    SELECT * FROM analysis_results 
                    WHERE symbol = ? AND analysis_type = ?
                    ORDER BY created_at DESC
                '''
                df = pd.read_sql_query(query, conn, params=(symbol, analysis_type))
            else:
                query = '''
                    SELECT * FROM analysis_results 
                    WHERE symbol = ?
                    ORDER BY created_at DESC
                '''
                df = pd.read_sql_query(query, conn, params=(symbol,))
            
            return df.to_dict('records') if not df.empty else []
    
    def get_user_balance(self, username):
        """Kullanıcı bakiyesini getir"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT balance FROM virtual_users WHERE username = ?', (username,))
            result = cursor.fetchone()
            return result[0] if result else 0.0
    
    def update_user_balance(self, username, new_balance):
        """Kullanıcı bakiyesini güncelle"""
        try:
            with sqlite3.connect(self.db_path, timeout=30.0, check_same_thread=False) as conn:
                conn.execute('PRAGMA journal_mode=WAL')
                conn.execute('PRAGMA synchronous=NORMAL')
                cursor = conn.cursor()
                cursor.execute('''
                    UPDATE virtual_users 
                    SET balance = ?, updated_at = CURRENT_TIMESTAMP
                    WHERE username = ?
                ''', (new_balance, username))
                conn.commit()
        except Exception as e:
            print(f"Bakiye güncelleme hatası: {e}")
            return False
        return True
    
    def buy_stock(self, username, symbol, shares, price):
        """Hisse satın al"""
        try:
            total_cost = shares * price
            current_balance = self.get_user_balance(username)
            
            if current_balance < total_cost:
                return False, "Yetersiz bakiye"
            
            with sqlite3.connect(self.db_path, timeout=30.0, check_same_thread=False) as conn:
                conn.execute('PRAGMA journal_mode=WAL')
                conn.execute('PRAGMA synchronous=NORMAL')
                cursor = conn.cursor()
                
                # Kullanıcı ID'sini al
                cursor.execute('SELECT id FROM virtual_users WHERE username = ?', (username,))
                user_id = cursor.fetchone()[0]
                
                # Bakiyeyi doğrudan güncelle
                cursor.execute('''
                    UPDATE virtual_users 
                    SET balance = balance - ?, updated_at = CURRENT_TIMESTAMP
                    WHERE username = ?
                ''', (total_cost, username))
                
                # Portföye ekle
                cursor.execute('''
                    INSERT INTO virtual_portfolio (user_id, symbol, shares, avg_price, purchase_date)
                    VALUES (?, ?, ?, ?, ?)
                ''', (user_id, symbol, shares, price, datetime.now().strftime('%Y-%m-%d')))
                
                # İşlem geçmişine ekle
                cursor.execute('''
                    INSERT INTO virtual_transactions 
                    (user_id, symbol, transaction_type, shares, price, total_amount, transaction_date)
                    VALUES (?, ?, 'BUY', ?, ?, ?, ?)
                ''', (user_id, symbol, shares, price, total_cost, datetime.now().strftime('%Y-%m-%d')))
                
                # Performans takibini başlat
                cursor.execute('''
                    INSERT INTO virtual_performance 
                    (user_id, symbol, initial_investment, current_value, profit_loss, profit_loss_percent, tracking_start_date)
                    VALUES (?, ?, ?, ?, 0, 0, ?)
                ''', (user_id, symbol, total_cost, total_cost, datetime.now().strftime('%Y-%m-%d')))
                
                conn.commit()
                return True, "Alım işlemi başarılı"
        except Exception as e:
            print(f"Alım işlemi hatası: {e}")
            return False, f"Alım işlemi başarısız: {str(e)}"
    
    def sell_stock(self, username, symbol, shares, price):
        """Hisse sat"""
        try:
            with sqlite3.connect(self.db_path, timeout=30.0, check_same_thread=False) as conn:
                conn.execute('PRAGMA journal_mode=WAL')
                conn.execute('PRAGMA synchronous=NORMAL')
                cursor = conn.cursor()
                
                # Kullanıcı ID'sini al
                cursor.execute('SELECT id FROM virtual_users WHERE username = ?', (username,))
                user_id = cursor.fetchone()[0]
                
                # Portföyde hisse var mı kontrol et
                cursor.execute('''
                    SELECT shares, avg_price FROM virtual_portfolio 
                    WHERE user_id = ? AND symbol = ?
                ''', (user_id, symbol))
                
                portfolio_result = cursor.fetchone()
                if not portfolio_result:
                    return False, "Portföyde bu hisse bulunmuyor"
                
                current_shares, avg_price = portfolio_result
                
                if shares > current_shares:
                    return False, "Yetersiz hisse miktarı"
                
                total_revenue = shares * price
                
                # Bakiyeyi doğrudan güncelle
                cursor.execute('''
                    UPDATE virtual_users 
                    SET balance = balance + ?, updated_at = CURRENT_TIMESTAMP
                    WHERE username = ?
                ''', (total_revenue, username))
                
                # Portföyü güncelle
                remaining_shares = current_shares - shares
                if remaining_shares == 0:
                    cursor.execute('''
                        DELETE FROM virtual_portfolio 
                        WHERE user_id = ? AND symbol = ?
                    ''', (user_id, symbol))
                else:
                    cursor.execute('''
                        UPDATE virtual_portfolio 
                        SET shares = ? WHERE user_id = ? AND symbol = ?
                    ''', (remaining_shares, user_id, symbol))
                
                # İşlem geçmişine ekle
                cursor.execute('''
                    INSERT INTO virtual_transactions 
                    (user_id, symbol, transaction_type, shares, price, total_amount, transaction_date)
                    VALUES (?, ?, 'SELL', ?, ?, ?, ?)
                ''', (user_id, symbol, shares, price, total_revenue, datetime.now().strftime('%Y-%m-%d')))
                
                # Performans takibini güncelle
                profit_loss = total_revenue - (shares * avg_price)
                profit_loss_percent = (profit_loss / (shares * avg_price)) * 100 if shares * avg_price > 0 else 0
                
                cursor.execute('''
                    UPDATE virtual_performance 
                    SET current_value = current_value - ?, 
                        profit_loss = profit_loss + ?,
                        profit_loss_percent = ?,
                        tracking_end_date = ?,
                        status = 'completed'
                    WHERE user_id = ? AND symbol = ? AND status = 'active'
                ''', (shares * avg_price, profit_loss, profit_loss_percent, datetime.now().strftime('%Y-%m-%d'), user_id, symbol))
                
                conn.commit()
                return True, f"Satım işlemi başarılı. Kar/Zarar: {profit_loss:+.2f} TL (%{profit_loss_percent:+.2f})"
        except Exception as e:
            print(f"Satım işlemi hatası: {e}")
            return False, f"Satım işlemi başarısız: {str(e)}"
    
    def get_user_portfolio(self, username):
        """Kullanıcı portföyünü getir"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Kullanıcı ID'sini al
            cursor.execute('SELECT id FROM virtual_users WHERE username = ?', (username,))
            user_result = cursor.fetchone()
            if not user_result:
                return []
            
            user_id = user_result[0]
            
            # Portföyü getir
            cursor.execute('''
                SELECT symbol, shares, avg_price, purchase_date
                FROM virtual_portfolio 
                WHERE user_id = ?
                ORDER BY created_at DESC
            ''', (user_id,))
            
            portfolio = []
            for row in cursor.fetchall():
                portfolio.append({
                    'symbol': row[0],
                    'shares': row[1],
                    'avg_price': row[2],
                    'purchase_date': row[3]
                })
            
            return portfolio
    
    def get_user_transactions(self, username, limit=50):
        """Kullanıcı işlem geçmişini getir"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Kullanıcı ID'sini al
            cursor.execute('SELECT id FROM virtual_users WHERE username = ?', (username,))
            user_result = cursor.fetchone()
            if not user_result:
                return []
            
            user_id = user_result[0]
            
            # İşlem geçmişini getir
            cursor.execute('''
                SELECT symbol, transaction_type, shares, price, total_amount, transaction_date
                FROM virtual_transactions 
                WHERE user_id = ?
                ORDER BY created_at DESC
                LIMIT ?
            ''', (user_id, limit))
            
            transactions = []
            for row in cursor.fetchall():
                transactions.append({
                    'symbol': row[0],
                    'type': row[1],
                    'shares': row[2],
                    'price': row[3],
                    'total_amount': row[4],
                    'date': row[5]
                })
            
            return transactions
    
    def update_performance_tracking(self, username):
        """Performans takibini güncelle (günlük)"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Kullanıcı ID'sini al
            cursor.execute('SELECT id FROM virtual_users WHERE username = ?', (username,))
            user_result = cursor.fetchone()
            if not user_result:
                return
            
            user_id = user_result[0]
            
            # Aktif performans kayıtlarını güncelle
            cursor.execute('''
                SELECT id, symbol, tracking_start_date FROM virtual_performance 
                WHERE user_id = ? AND status = 'active'
            ''', (user_id,))
            
            for row in cursor.fetchall():
                perf_id, symbol, start_date = row
                
                # Gün sayısını hesapla
                start_dt = datetime.strptime(start_date, '%Y-%m-%d')
                days_held = (datetime.now() - start_dt).days
                
                # 7 gün kontrolü
                if days_held >= 7:
                    cursor.execute('''
                        UPDATE virtual_performance 
                        SET status = 'completed', days_held = ?, tracking_end_date = ?
                        WHERE id = ?
                    ''', (days_held, datetime.now().strftime('%Y-%m-%d'), perf_id))
                else:
                    cursor.execute('''
                        UPDATE virtual_performance 
                        SET days_held = ?
                        WHERE id = ?
                    ''', (days_held, perf_id))
            
            conn.commit()
    
    def get_performance_summary(self, username):
        """Kullanıcının performans özetini getir"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Kullanıcı ID'sini al
            cursor.execute('SELECT id FROM virtual_users WHERE username = ?', (username,))
            user_id = cursor.fetchone()[0]
            
            query = '''
                SELECT symbol, initial_investment, current_value, profit_loss, profit_loss_percent, tracking_start_date
                FROM virtual_performance 
                WHERE user_id = ? AND status = 'active'
                ORDER BY profit_loss_percent DESC
            '''
            
            df = pd.read_sql_query(query, conn, params=(user_id,))
            return df.to_dict('records') if not df.empty else []
    
    def get_all_users(self):
        """Tüm kullanıcıları getir"""
        with sqlite3.connect(self.db_path) as conn:
            query = 'SELECT username, balance FROM virtual_users ORDER BY username'
            df = pd.read_sql_query(query, conn)
            return df.to_dict('records') if not df.empty else []
    
    # Watchlist fonksiyonları
    def add_to_watchlist(self, symbol, name=""):
        """Takip listesine hisse ekle"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Watchlist tablosunu oluştur
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS watchlist (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    symbol TEXT UNIQUE NOT NULL,
                    name TEXT,
                    added_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            try:
                cursor.execute('''
                    INSERT INTO watchlist (symbol, name)
                    VALUES (?, ?)
                ''', (symbol, name))
                conn.commit()
                return True
            except sqlite3.IntegrityError:
                return False  # Zaten mevcut
    
    def remove_from_watchlist(self, symbol):
        """Takip listesinden hisse çıkar"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('DELETE FROM watchlist WHERE symbol = ?', (symbol,))
            conn.commit()
            return cursor.rowcount > 0
    
    def get_watchlist(self):
        """Takip listesini getir"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Watchlist tablosunu oluştur
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS watchlist (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    symbol TEXT UNIQUE NOT NULL,
                    name TEXT,
                    added_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            query = 'SELECT symbol, name, added_date FROM watchlist ORDER BY added_date DESC'
            df = pd.read_sql_query(query, conn)
            return df.to_dict('records') if not df.empty else []
    
    def save_news_data(self, news_data):
        """Haber verilerini kaydet"""
        # Bu fonksiyon şimdilik boş bırakılıyor
        pass 

    def get_performance_tracking(self, username, days=7):
        """7 günlük performans takibi"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Kullanıcı ID'sini al
            cursor.execute('SELECT id FROM virtual_users WHERE username = ?', (username,))
            user_result = cursor.fetchone()
            if not user_result:
                return []
            
            user_id = user_result[0]
            
            # Performans verilerini getir
            cursor.execute('''
                SELECT symbol, initial_investment, current_value, profit_loss, profit_loss_percent, 
                       tracking_start_date, days_held, status
                FROM virtual_performance 
                WHERE user_id = ? AND status = 'active'
                ORDER BY created_at DESC
            ''', (user_id,))
            
            performance = []
            for row in cursor.fetchall():
                # Gün sayısını hesapla
                start_date = datetime.strptime(row[5], '%Y-%m-%d')
                days_held = (datetime.now() - start_date).days
                
                performance.append({
                    'symbol': row[0],
                    'initial_investment': row[1],
                    'current_value': row[2],
                    'profit_loss': row[3],
                    'profit_loss_percent': row[4],
                    'start_date': row[5],
                    'days_held': days_held,
                    'status': row[7]
                })
            
            return performance
    
    def get_news_for_symbol(self, symbol, limit=10):
        """Hisse için haber verilerini getir"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT title, sentiment, sentiment_score, source, url, timestamp
                FROM news_data 
                WHERE symbol = ?
                ORDER BY timestamp DESC
                LIMIT ?
            ''', (symbol, limit))
            
            news = []
            for row in cursor.fetchall():
                news.append({
                    'title': row[0],
                    'sentiment': row[1],
                    'sentiment_score': row[2],
                    'source': row[3],
                    'url': row[4],
                    'date': row[5]
                })
            
            return news if news else self._get_mock_news(symbol)
    
    def _get_mock_news(self, symbol):
        """Mock haber verisi oluşturur"""
        import random
        
        news_templates = [
            f"{symbol} hissesi güçlü performans gösteriyor",
            f"{symbol} için yeni yatırım fırsatları",
            f"{symbol} şirketinin çeyreklik sonuçları beklentileri aştı",
            f"{symbol} hissesinde teknik analiz sinyalleri",
            f"{symbol} için piyasa uzmanlarından öneriler"
        ]
        
        news = []
        for i in range(5):
            news.append({
                'title': news_templates[i % len(news_templates)],
                'sentiment': random.choice(['positive', 'negative', 'neutral']),
                'sentiment_score': random.uniform(-1, 1),
                'source': f"Kaynak {i+1}",
                'url': f"https://example.com/news/{i+1}",
                'date': (datetime.now() - timedelta(days=i)).strftime('%Y-%m-%d')
            })
        
        return news 