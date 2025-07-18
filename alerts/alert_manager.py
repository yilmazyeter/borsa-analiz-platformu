"""
Fiyat Alarmları Yönetim Modülü
Kullanıcı alarmları oluşturma ve yönetme
"""

import sqlite3
import json
from datetime import datetime, timedelta
import threading
import time

class AlertManager:
    """Fiyat alarmları yönetim sınıfı"""
    
    def __init__(self, db_path='data/alerts.db'):
        self.db_path = db_path
        self.alerts = {}
        self.active_alerts = {}
        self.monitoring_thread = None
        self.is_monitoring = False
        
        # Veritabanını başlat
        self._init_database()
    
    def _init_database(self):
        """Veritabanını başlatır"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Alarm tablosu oluştur
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS alerts (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id TEXT NOT NULL,
                    symbol TEXT NOT NULL,
                    alert_type TEXT NOT NULL,
                    target_price REAL NOT NULL,
                    condition TEXT NOT NULL,
                    is_active BOOLEAN DEFAULT 1,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    triggered_at TIMESTAMP NULL,
                    notification_sent BOOLEAN DEFAULT 0
                )
            ''')
            
            # Alarm geçmişi tablosu
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS alert_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    alert_id INTEGER,
                    symbol TEXT NOT NULL,
                    target_price REAL NOT NULL,
                    current_price REAL NOT NULL,
                    triggered_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (alert_id) REFERENCES alerts (id)
                )
            ''')
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            print(f"Veritabanı başlatma hatası: {str(e)}")
    
    def create_alert(self, user_id, symbol, alert_type, target_price, condition='above'):
        """
        Yeni alarm oluşturur
        
        Args:
            user_id (str): Kullanıcı ID
            symbol (str): Hisse sembolü
            alert_type (str): Alarm türü ('price', 'percentage', 'volume')
            target_price (float): Hedef fiyat
            condition (str): Koşul ('above', 'below', 'equals')
            
        Returns:
            dict: Oluşturulan alarm bilgisi
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO alerts (user_id, symbol, alert_type, target_price, condition)
                VALUES (?, ?, ?, ?, ?)
            ''', (user_id, symbol, alert_type, target_price, condition))
            
            alert_id = cursor.lastrowid
            conn.commit()
            conn.close()
            
            alert = {
                'id': alert_id,
                'user_id': user_id,
                'symbol': symbol,
                'alert_type': alert_type,
                'target_price': target_price,
                'condition': condition,
                'is_active': True,
                'created_at': datetime.now().isoformat()
            }
            
            # Aktif alarmlara ekle
            self.active_alerts[alert_id] = alert
            
            return alert
            
        except Exception as e:
            print(f"Alarm oluşturma hatası: {str(e)}")
            return None
    
    def get_user_alerts(self, user_id):
        """
        Kullanıcının alarmlarını getirir
        
        Args:
            user_id (str): Kullanıcı ID
            
        Returns:
            list: Kullanıcı alarmları
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT id, symbol, alert_type, target_price, condition, is_active, created_at, triggered_at
                FROM alerts
                WHERE user_id = ?
                ORDER BY created_at DESC
            ''', (user_id,))
            
            alerts = []
            for row in cursor.fetchall():
                alert = {
                    'id': row[0],
                    'symbol': row[1],
                    'alert_type': row[2],
                    'target_price': row[3],
                    'condition': row[4],
                    'is_active': bool(row[5]),
                    'created_at': row[6],
                    'triggered_at': row[7]
                }
                alerts.append(alert)
            
            conn.close()
            return alerts
            
        except Exception as e:
            print(f"Alarm getirme hatası: {str(e)}")
            return []
    
    def update_alert(self, alert_id, **kwargs):
        """
        Alarm günceller
        
        Args:
            alert_id (int): Alarm ID
            **kwargs: Güncellenecek alanlar
            
        Returns:
            bool: Başarı durumu
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Güncellenecek alanları hazırla
            update_fields = []
            values = []
            
            for key, value in kwargs.items():
                if key in ['target_price', 'condition', 'is_active']:
                    update_fields.append(f"{key} = ?")
                    values.append(value)
            
            if not update_fields:
                return False
            
            values.append(alert_id)
            
            query = f"UPDATE alerts SET {', '.join(update_fields)} WHERE id = ?"
            cursor.execute(query, values)
            
            conn.commit()
            conn.close()
            
            # Aktif alarmları güncelle
            if alert_id in self.active_alerts:
                self.active_alerts[alert_id].update(kwargs)
            
            return True
            
        except Exception as e:
            print(f"Alarm güncelleme hatası: {str(e)}")
            return False
    
    def delete_alert(self, alert_id):
        """
        Alarm siler
        
        Args:
            alert_id (int): Alarm ID
            
        Returns:
            bool: Başarı durumu
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('DELETE FROM alerts WHERE id = ?', (alert_id,))
            
            conn.commit()
            conn.close()
            
            # Aktif alarmlardan kaldır
            if alert_id in self.active_alerts:
                del self.active_alerts[alert_id]
            
            return True
            
        except Exception as e:
            print(f"Alarm silme hatası: {str(e)}")
            return False
    
    def check_alerts(self, current_prices):
        """
        Aktif alarmları kontrol eder
        
        Args:
            current_prices (dict): Güncel fiyatlar {symbol: price}
            
        Returns:
            list: Tetiklenen alarmlar
        """
        triggered_alerts = []
        
        try:
            for alert_id, alert in self.active_alerts.items():
                if not alert['is_active']:
                    continue
                
                symbol = alert['symbol']
                if symbol not in current_prices:
                    continue
                
                current_price = current_prices[symbol]
                target_price = alert['target_price']
                condition = alert['condition']
                
                # Koşul kontrolü
                is_triggered = False
                
                if condition == 'above' and current_price >= target_price:
                    is_triggered = True
                elif condition == 'below' and current_price <= target_price:
                    is_triggered = True
                elif condition == 'equals' and abs(current_price - target_price) < 0.01:
                    is_triggered = True
                
                if is_triggered:
                    # Alarm geçmişine kaydet
                    self._record_alert_trigger(alert_id, symbol, target_price, current_price)
                    
                    # Alarmı devre dışı bırak
                    self.update_alert(alert_id, is_active=False, triggered_at=datetime.now().isoformat())
                    
                    triggered_alerts.append({
                        'alert_id': alert_id,
                        'symbol': symbol,
                        'target_price': target_price,
                        'current_price': current_price,
                        'condition': condition,
                        'user_id': alert['user_id']
                    })
            
            return triggered_alerts
            
        except Exception as e:
            print(f"Alarm kontrol hatası: {str(e)}")
            return []
    
    def _record_alert_trigger(self, alert_id, symbol, target_price, current_price):
        """Alarm tetiklenmesini kaydeder"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO alert_history (alert_id, symbol, target_price, current_price)
                VALUES (?, ?, ?, ?)
            ''', (alert_id, symbol, target_price, current_price))
            
            conn.commit()
            conn.close()
            
        except Exception as e:
            print(f"Alarm tetikleme kayıt hatası: {str(e)}")
    
    def get_alert_history(self, user_id, limit=20):
        """
        Alarm geçmişini getirir
        
        Args:
            user_id (str): Kullanıcı ID
            limit (int): Maksimum kayıt sayısı
            
        Returns:
            list: Alarm geçmişi
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT ah.symbol, ah.target_price, ah.current_price, ah.triggered_at,
                       a.condition, a.alert_type
                FROM alert_history ah
                JOIN alerts a ON ah.alert_id = a.id
                WHERE a.user_id = ?
                ORDER BY ah.triggered_at DESC
                LIMIT ?
            ''', (user_id, limit))
            
            history = []
            for row in cursor.fetchall():
                history.append({
                    'symbol': row[0],
                    'target_price': row[1],
                    'current_price': row[2],
                    'triggered_at': row[3],
                    'condition': row[4],
                    'alert_type': row[5]
                })
            
            conn.close()
            return history
            
        except Exception as e:
            print(f"Alarm geçmişi getirme hatası: {str(e)}")
            return []
    
    def start_monitoring(self, price_callback):
        """
        Alarm izlemeyi başlatır
        
        Args:
            price_callback (function): Fiyat verisi çekme fonksiyonu
        """
        if self.is_monitoring:
            return
        
        self.is_monitoring = True
        self.monitoring_thread = threading.Thread(target=self._monitor_alerts, args=(price_callback,))
        self.monitoring_thread.daemon = True
        self.monitoring_thread.start()
    
    def stop_monitoring(self):
        """Alarm izlemeyi durdurur"""
        self.is_monitoring = False
        if self.monitoring_thread:
            self.monitoring_thread.join()
    
    def _monitor_alerts(self, price_callback):
        """Alarm izleme döngüsü"""
        while self.is_monitoring:
            try:
                # Güncel fiyatları al
                current_prices = price_callback()
                
                if current_prices:
                    # Alarmları kontrol et
                    triggered_alerts = self.check_alerts(current_prices)
                    
                    # Tetiklenen alarmları işle
                    for alert in triggered_alerts:
                        self._handle_triggered_alert(alert)
                
                # 30 saniye bekle
                time.sleep(30)
                
            except Exception as e:
                print(f"Alarm izleme hatası: {str(e)}")
                time.sleep(60)  # Hata durumunda 1 dakika bekle
    
    def _handle_triggered_alert(self, alert):
        """Tetiklenen alarmı işler"""
        try:
            # Bildirim gönder
            message = f"🚨 ALARM: {alert['symbol']} fiyatı {alert['current_price']:.2f} oldu!"
            message += f" (Hedef: {alert['target_price']:.2f})"
            
            print(f"ALARM TETİKLENDİ: {message}")
            
            # Burada e-posta, SMS veya push notification gönderilebilir
            # self.notification_system.send_notification(alert['user_id'], message)
            
        except Exception as e:
            print(f"Alarm işleme hatası: {str(e)}")
    
    def get_alert_statistics(self, user_id):
        """
        Alarm istatistiklerini getirir
        
        Args:
            user_id (str): Kullanıcı ID
            
        Returns:
            dict: İstatistikler
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Toplam alarm sayısı
            cursor.execute('SELECT COUNT(*) FROM alerts WHERE user_id = ?', (user_id,))
            total_alerts = cursor.fetchone()[0]
            
            # Aktif alarm sayısı
            cursor.execute('SELECT COUNT(*) FROM alerts WHERE user_id = ? AND is_active = 1', (user_id,))
            active_alerts = cursor.fetchone()[0]
            
            # Tetiklenen alarm sayısı
            cursor.execute('''
                SELECT COUNT(*) FROM alerts 
                WHERE user_id = ? AND triggered_at IS NOT NULL
            ''', (user_id,))
            triggered_alerts = cursor.fetchone()[0]
            
            # En çok alarm verilen hisseler
            cursor.execute('''
                SELECT symbol, COUNT(*) as count
                FROM alerts
                WHERE user_id = ?
                GROUP BY symbol
                ORDER BY count DESC
                LIMIT 5
            ''', (user_id,))
            top_symbols = [{'symbol': row[0], 'count': row[1]} for row in cursor.fetchall()]
            
            conn.close()
            
            return {
                'total_alerts': total_alerts,
                'active_alerts': active_alerts,
                'triggered_alerts': triggered_alerts,
                'top_symbols': top_symbols
            }
            
        except Exception as e:
            print(f"İstatistik getirme hatası: {str(e)}")
            return {
                'total_alerts': 0,
                'active_alerts': 0,
                'triggered_alerts': 0,
                'top_symbols': []
            } 