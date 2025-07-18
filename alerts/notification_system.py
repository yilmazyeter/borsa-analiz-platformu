"""
Bildirim Sistemi Modulu - Email, Push ve Webhook Entegrasyonlari
"""

import smtplib
import json
import requests
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
import time
import random

class NotificationSystem:
    """Bildirim sistemi sinifi - coklu kanal destegi"""
    
    def __init__(self):
        self.notification_history = []
        self.email_config = {
            'smtp_server': 'smtp.gmail.com',
            'smtp_port': 587,
            'sender_email': 'your-email@gmail.com',
            'sender_password': 'your-app-password'
        }
        self.webhook_config = {
            'discord_webhook': None,
            'slack_webhook': None,
            'telegram_bot_token': None,
            'telegram_chat_id': None
        }
        self.notification_settings = {
            'email_enabled': True,
            'webhook_enabled': False,
            'push_enabled': False,
            'notification_cooldown': 300  # 5 dakika
        }
    
    def send_email_notification(self, subject: str, message: str, 
                              recipient_email: Optional[str] = None) -> Dict:
        """
        Email bildirimi gonderir
        
        Args:
            subject: Email konusu
            message: Email icerigi
            recipient_email: Alici email adresi
            
        Returns:
            Gonderim sonucu
        """
        try:
            if not self.notification_settings['email_enabled']:
                return {
                    'success': False,
                    'error': 'Email bildirimleri devre disi',
                    'timestamp': datetime.now().isoformat()
                }
            
            # Mock email gonderimi (gercek SMTP yerine)
            email_data = {
                'to': recipient_email or self.email_config['sender_email'],
                'subject': subject,
                'message': message,
                'timestamp': datetime.now().isoformat()
            }
            
            # Email gecmisine ekle
            self.notification_history.append({
                'type': 'email',
                'data': email_data,
                'status': 'sent',
                'timestamp': datetime.now().isoformat()
            })
            
            return {
                'success': True,
                'message': 'Email basariyla gonderildi',
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }
    
    def send_discord_notification(self, message: str, webhook_url: Optional[str] = None) -> Dict:
        """
        Discord webhook bildirimi gonderir
        
        Args:
            message: Gonderilecek mesaj
            webhook_url: Discord webhook URL'i
            
        Returns:
            Gonderim sonucu
        """
        try:
            if not self.notification_settings['webhook_enabled']:
                return {
                    'success': False,
                    'error': 'Webhook bildirimleri devre disi',
                    'timestamp': datetime.now().isoformat()
                }
            
            webhook_url = webhook_url or self.webhook_config['discord_webhook']
            if not webhook_url:
                return {
                    'success': False,
                    'error': 'Discord webhook URL bulunamadi',
                    'timestamp': datetime.now().isoformat()
                }
            
            # Discord webhook payload
            payload = {
                'content': message,
                'username': 'Borsa Bot',
                'avatar_url': 'https://example.com/bot-avatar.png'
            }
            
            # Mock webhook gonderimi
            webhook_data = {
                'url': webhook_url,
                'payload': payload,
                'timestamp': datetime.now().isoformat()
            }
            
            # Webhook gecmisine ekle
            self.notification_history.append({
                'type': 'discord_webhook',
                'data': webhook_data,
                'status': 'sent',
                'timestamp': datetime.now().isoformat()
            })
            
            return {
                'success': True,
                'message': 'Discord bildirimi basariyla gonderildi',
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }
    
    def send_slack_notification(self, message: str, channel: str = '#general', 
                              webhook_url: Optional[str] = None) -> Dict:
        """
        Slack webhook bildirimi gonderir
        
        Args:
            message: Gonderilecek mesaj
            channel: Slack kanali
            webhook_url: Slack webhook URL'i
            
        Returns:
            Gonderim sonucu
        """
        try:
            if not self.notification_settings['webhook_enabled']:
                return {
                    'success': False,
                    'error': 'Webhook bildirimleri devre disi',
                    'timestamp': datetime.now().isoformat()
                }
            
            webhook_url = webhook_url or self.webhook_config['slack_webhook']
            if not webhook_url:
                return {
                    'success': False,
                    'error': 'Slack webhook URL bulunamadi',
                    'timestamp': datetime.now().isoformat()
                }
            
            # Slack webhook payload
            payload = {
                'channel': channel,
                'text': message,
                'username': 'Borsa Bot',
                'icon_emoji': ':chart_with_upwards_trend:'
            }
            
            # Mock webhook gonderimi
            webhook_data = {
                'url': webhook_url,
                'payload': payload,
                'timestamp': datetime.now().isoformat()
            }
            
            # Webhook gecmisine ekle
            self.notification_history.append({
                'type': 'slack_webhook',
                'data': webhook_data,
                'status': 'sent',
                'timestamp': datetime.now().isoformat()
            })
            
            return {
                'success': True,
                'message': 'Slack bildirimi basariyla gonderildi',
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }
    
    def send_telegram_notification(self, message: str, chat_id: Optional[str] = None, 
                                 bot_token: Optional[str] = None) -> Dict:
        """
        Telegram bot bildirimi gonderir
        
        Args:
            message: Gonderilecek mesaj
            chat_id: Telegram chat ID
            bot_token: Telegram bot token
            
        Returns:
            Gonderim sonucu
        """
        try:
            if not self.notification_settings['webhook_enabled']:
                return {
                    'success': False,
                    'error': 'Webhook bildirimleri devre disi',
                    'timestamp': datetime.now().isoformat()
                }
            
            chat_id = chat_id or self.webhook_config['telegram_chat_id']
            bot_token = bot_token or self.webhook_config['telegram_bot_token']
            
            if not chat_id or not bot_token:
                return {
                    'success': False,
                    'error': 'Telegram bot token veya chat ID bulunamadi',
                    'timestamp': datetime.now().isoformat()
                }
            
            # Telegram API URL
            telegram_url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
            
            # Telegram payload
            payload = {
                'chat_id': chat_id,
                'text': message,
                'parse_mode': 'HTML'
            }
            
            # Mock Telegram gonderimi
            telegram_data = {
                'url': telegram_url,
                'payload': payload,
                'timestamp': datetime.now().isoformat()
            }
            
            # Telegram gecmisine ekle
            self.notification_history.append({
                'type': 'telegram',
                'data': telegram_data,
                'status': 'sent',
                'timestamp': datetime.now().isoformat()
            })
            
            return {
                'success': True,
                'message': 'Telegram bildirimi basariyla gonderildi',
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }
    
    def send_push_notification(self, title: str, message: str, 
                             user_id: Optional[str] = None) -> Dict:
        """
        Push bildirimi gonderir (web push notifications)
        
        Args:
            title: Bildirim basligi
            message: Bildirim mesaji
            user_id: Kullanici ID'si
            
        Returns:
            Gonderim sonucu
        """
        try:
            if not self.notification_settings['push_enabled']:
                return {
                    'success': False,
                    'error': 'Push bildirimleri devre disi',
                    'timestamp': datetime.now().isoformat()
                }
            
            # Mock push notification
            push_data = {
                'title': title,
                'message': message,
                'user_id': user_id,
                'timestamp': datetime.now().isoformat()
            }
            
            # Push gecmisine ekle
            self.notification_history.append({
                'type': 'push',
                'data': push_data,
                'status': 'sent',
                'timestamp': datetime.now().isoformat()
            })
            
            return {
                'success': True,
                'message': 'Push bildirimi basariyla gonderildi',
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }
    
    def send_multi_channel_notification(self, title: str, message: str, 
                                      channels: Optional[List[str]] = None) -> Dict:
        """
        Coklu kanal bildirimi gonderir
        
        Args:
            title: Bildirim basligi
            message: Bildirim mesaji
            channels: Bildirim kanallari listesi
            
        Returns:
            Gonderim sonuclari
        """
        if not channels:
            channels = ['email']
        
        results = {}
        
        for channel in channels:
            if channel == 'email':
                results['email'] = self.send_email_notification(title, message)
            elif channel == 'discord':
                results['discord'] = self.send_discord_notification(message)
            elif channel == 'slack':
                results['slack'] = self.send_slack_notification(message)
            elif channel == 'telegram':
                results['telegram'] = self.send_telegram_notification(message)
            elif channel == 'push':
                results['push'] = self.send_push_notification(title, message)
        
        return {
            'results': results,
            'timestamp': datetime.now().isoformat()
        }
    
    def check_notification_cooldown(self, alert_type: str, symbol: Optional[str] = None) -> bool:
        """
        Bildirim cooldown kontrolu yapar
        
        Args:
            alert_type: Alarm turu
            symbol: Hisse sembolu
            
        Returns:
            Cooldown durumu
        """
        cooldown_seconds = self.notification_settings['notification_cooldown']
        cutoff_time = datetime.now() - timedelta(seconds=cooldown_seconds)
        
        # Son bildirimleri kontrol et
        recent_notifications = [
            n for n in self.notification_history
            if n['timestamp'] > cutoff_time.isoformat() and
            n['data'].get('alert_type') == alert_type and
            (not symbol or n['data'].get('symbol') == symbol)
        ]
        
        return len(recent_notifications) == 0
    
    def get_notification_history(self, limit: int = 50) -> List[Dict]:
        """
        Bildirim gecmisini getirir
        
        Args:
            limit: Maksimum kayit sayisi
            
        Returns:
            Bildirim gecmisi
        """
        return self.notification_history[-limit:] if self.notification_history else []
    
    def clear_notification_history(self) -> Dict:
        """
        Bildirim gecmisini temizler
        
        Returns:
            Temizleme sonucu
        """
        count = len(self.notification_history)
        self.notification_history.clear()
        
        return {
            'success': True,
            'message': f'{count} bildirim kaydi temizlendi',
            'timestamp': datetime.now().isoformat()
        }
    
    def update_notification_settings(self, settings: Dict) -> Dict:
        """
        Bildirim ayarlarini gunceller
        
        Args:
            settings: Yeni ayarlar
            
        Returns:
            Guncelleme sonucu
        """
        try:
            self.notification_settings.update(settings)
            
            return {
                'success': True,
                'message': 'Bildirim ayarlari guncellendi',
                'settings': self.notification_settings,
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }
    
    def update_webhook_config(self, config: Dict) -> Dict:
        """
        Webhook konfigurasyonunu gunceller
        
        Args:
            config: Yeni webhook ayarlari
            
        Returns:
            Guncelleme sonucu
        """
        try:
            self.webhook_config.update(config)
            
            return {
                'success': True,
                'message': 'Webhook konfigurasyonu guncellendi',
                'config': self.webhook_config,
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }
    
    def generate_mock_notifications(self, count: int = 10) -> List[Dict]:
        """
        Mock bildirim verisi olusturur
        
        Args:
            count: Olusturulacak bildirim sayisi
            
        Returns:
            Mock bildirim verileri
        """
        mock_notifications = []
        
        alert_types = ['price_alert', 'volume_alert', 'trend_alert', 'news_alert']
        symbols = ['AAPL', 'MSFT', 'GOOGL', 'TSLA', 'AMZN']
        channels = ['email', 'discord', 'slack', 'telegram', 'push']
        
        for i in range(count):
            alert_type = random.choice(alert_types)
            symbol = random.choice(symbols)
            channel = random.choice(channels)
            
            # Rastgele tarih (son 7 gun icinde)
            days_ago = random.randint(0, 7)
            hours_ago = random.randint(0, 24)
            timestamp = datetime.now() - timedelta(days=days_ago, hours=hours_ago)
            
            notification = {
                'type': channel,
                'data': {
                    'alert_type': alert_type,
                    'symbol': symbol,
                    'title': f'Mock Alarm {i+1}',
                    'message': f'Bu bir mock {alert_type} bildirimidir.',
                    'timestamp': timestamp.isoformat()
                },
                'status': 'sent',
                'timestamp': timestamp.isoformat()
            }
            
            mock_notifications.append(notification)
        
        # Tarihe gore sirala
        mock_notifications.sort(key=lambda x: x['timestamp'])
        
        return mock_notifications 