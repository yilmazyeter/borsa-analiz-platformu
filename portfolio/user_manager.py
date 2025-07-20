#!/usr/bin/env python3
"""
Kullanıcı Yönetimi ve Portföy Sistemi
"""

import json
import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import logging
from .exchange_rate import exchange_rate_service

class UserManager:
    def __init__(self, data_dir: str = "data"):
        self.data_dir = data_dir
        self.users_file = os.path.join(data_dir, "users.json")
        self.portfolios_file = os.path.join(data_dir, "portfolios.json")
        self.watchlists_file = os.path.join(data_dir, "watchlists.json")
        self.transactions_file = os.path.join(data_dir, "transactions.json")
        
        # Logging
        self.logger = logging.getLogger(__name__)
        
        # Dosyaları oluştur
        self._initialize_files()
        
        # Varsayılan kullanıcıları oluştur
        self._create_default_users()
    
    def _initialize_files(self):
        """Gerekli dosyaları oluşturur"""
        os.makedirs(self.data_dir, exist_ok=True)
        
        # Kullanıcılar dosyası
        if not os.path.exists(self.users_file):
            default_users = {
                "gokhan": {
                    "name": "Gökhan",
                    "balance": 500000.0,  # 500K USD
                    "created_at": datetime.now().isoformat(),
                    "last_login": None
                },
                "ugur": {
                    "name": "Uğur", 
                    "balance": 500000.0,  # 500K USD
                    "created_at": datetime.now().isoformat(),
                    "last_login": None
                }
            }
            self._save_json(self.users_file, default_users)
        
        # Portföyler dosyası
        if not os.path.exists(self.portfolios_file):
            default_portfolios = {
                "gokhan": {},
                "ugur": {}
            }
            self._save_json(self.portfolios_file, default_portfolios)
        
        # Takip listeleri dosyası
        if not os.path.exists(self.watchlists_file):
            default_watchlists = {
                "gokhan": [],
                "ugur": []
            }
            self._save_json(self.watchlists_file, default_watchlists)
        
        # İşlemler dosyası
        if not os.path.exists(self.transactions_file):
            default_transactions = {
                "gokhan": [],
                "ugur": []
            }
            self._save_json(self.transactions_file, default_transactions)
    
    def _create_default_users(self):
        """Varsayılan kullanıcıları oluşturur"""
        users = self._load_json(self.users_file)
        if not users:
            self._initialize_files()
    
    def _load_json(self, file_path: str) -> Dict:
        """JSON dosyasını yükler"""
        try:
            if os.path.exists(file_path):
                with open(file_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            return {}
        except Exception as e:
            self.logger.error(f"JSON yükleme hatası {file_path}: {e}")
            return {}
    
    def _save_json(self, file_path: str, data: Dict):
        """JSON dosyasına kaydeder"""
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            self.logger.error(f"JSON kaydetme hatası {file_path}: {e}")
    
    def get_users(self) -> Dict:
        """Tüm kullanıcıları döndürür"""
        return self._load_json(self.users_file)
    
    def get_user(self, username: str) -> Optional[Dict]:
        """Belirli bir kullanıcıyı döndürür"""
        users = self.get_users()
        return users.get(username)
    
    def get_user_balance(self, username: str) -> float:
        """Kullanıcının bakiyesini döndürür"""
        user = self.get_user(username)
        return user.get('balance', 0.0) if user else 0.0
    
    def update_user_balance(self, username: str, new_balance: float):
        """Kullanıcı bakiyesini günceller"""
        users = self.get_users()
        if username in users:
            users[username]['balance'] = new_balance
            self._save_json(self.users_file, users)
            self.logger.info(f"{username} bakiyesi güncellendi: {new_balance:.2f} TL")
    
    def reset_user_balance(self, username: str, balance: float = 500000.0):
        """Kullanıcı bakiyesini sıfırlar (varsayılan: 500K USD)"""
        users = self.get_users()
        if username in users:
            users[username]['balance'] = balance
            self._save_json(self.users_file, users)
            self.logger.info(f"{username} bakiyesi sıfırlandı: {balance:.2f} TL")
    
    def get_portfolio(self, username: str) -> Dict:
        """Kullanıcının portföyünü döndürür"""
        portfolios = self._load_json(self.portfolios_file)
        return portfolios.get(username, {})
    
    def update_portfolio(self, username: str, portfolio: Dict):
        """Kullanıcı portföyünü günceller"""
        portfolios = self._load_json(self.portfolios_file)
        portfolios[username] = portfolio
        self._save_json(self.portfolios_file, portfolios)
    
    def get_watchlist(self, username: str) -> List[str]:
        """Kullanıcının takip listesini döndürür"""
        watchlists = self._load_json(self.watchlists_file)
        return watchlists.get(username, [])
    
    def add_to_watchlist(self, username: str, symbol: str):
        """Takip listesine coin ekler"""
        watchlists = self._load_json(self.watchlists_file)
        if username not in watchlists:
            watchlists[username] = []
        
        if symbol not in watchlists[username]:
            watchlists[username].append(symbol)
            self._save_json(self.watchlists_file, watchlists)
            self.logger.info(f"{username} takip listesine {symbol} eklendi")
    
    def remove_from_watchlist(self, username: str, symbol: str):
        """Takip listesinden coin çıkarır"""
        watchlists = self._load_json(self.watchlists_file)
        if username in watchlists and symbol in watchlists[username]:
            watchlists[username].remove(symbol)
            self._save_json(self.watchlists_file, watchlists)
            self.logger.info(f"{username} takip listesinden {symbol} çıkarıldı")
    
    def get_transactions(self, username: str) -> List[Dict]:
        """Kullanıcının işlem geçmişini döndürür"""
        transactions = self._load_json(self.transactions_file)
        return transactions.get(username, [])
    
    def add_transaction(self, username: str, transaction: Dict):
        """İşlem geçmişine yeni işlem ekler"""
        transactions = self._load_json(self.transactions_file)
        if username not in transactions:
            transactions[username] = []
        
        # İşlem tarihini ekle
        transaction['timestamp'] = datetime.now().isoformat()
        transaction['id'] = len(transactions[username]) + 1
        
        transactions[username].append(transaction)
        self._save_json(self.transactions_file, transactions)
        self.logger.info(f"{username} için yeni işlem eklendi: {transaction['type']} {transaction['symbol']}")
    
    def buy_crypto(self, username: str, symbol: str, amount_usdt: float, price: float) -> bool:
        """Kripto para satın alma işlemi"""
        try:
            user = self.get_user(username)
            if not user:
                return False
            
            current_balance = user['balance']
            # Bakiye USD olduğu için doğrudan USDT miktarını kullan
            total_cost_usd = amount_usdt
            
            if total_cost_usd > current_balance:
                self.logger.warning(f"{username} yetersiz bakiye: {current_balance:.2f} USD, gerekli: {total_cost_usd:.2f} USD")
                return False
            
            # Bakiyeyi güncelle
            new_balance = current_balance - total_cost_usd
            self.update_user_balance(username, new_balance)
            
            # Portföyü güncelle
            portfolio = self.get_portfolio(username)
            if symbol not in portfolio:
                portfolio[symbol] = {
                    'amount': 0.0,
                    'avg_price': 0.0,
                    'total_invested': 0.0
                }
            
            # Ortalama fiyat hesapla (USD bazında)
            current_amount = portfolio[symbol]['amount']
            current_avg_price = portfolio[symbol]['avg_price']
            current_invested = portfolio[symbol]['total_invested']
            
            # Coin miktarını hesapla (USDT / fiyat)
            coin_amount = amount_usdt / price
            new_amount = current_amount + coin_amount
            new_invested = current_invested + total_cost_usd
            new_avg_price = new_invested / new_amount if new_amount > 0 else 0
            
            portfolio[symbol] = {
                'amount': new_amount,
                'avg_price': new_avg_price,
                'total_invested': new_invested
            }
            
            self.update_portfolio(username, portfolio)
            
            # İşlem kaydı ekle
            transaction = {
                'type': 'BUY',
                'symbol': symbol,
                'amount': coin_amount,
                'price': price,
                'total_cost': total_cost_usd,
                'balance_after': new_balance
            }
            self.add_transaction(username, transaction)
            
            self.logger.info(f"{username} {coin_amount:.6f} {symbol} satın aldı: ${price:.6f} (${total_cost_usd:.2f})")
            return True
            
        except Exception as e:
            self.logger.error(f"Satın alma işlemi hatası: {e}")
            return False
    
    def sell_crypto(self, username: str, symbol: str, amount_usdt: float, price: float) -> bool:
        """Kripto para satma işlemi"""
        try:
            user = self.get_user(username)
            if not user:
                return False
            
            portfolio = self.get_portfolio(username)
            if symbol not in portfolio or portfolio[symbol]['amount'] < amount_usdt:
                self.logger.warning(f"{username} yetersiz {symbol} miktarı")
                return False
            
            current_balance = user['balance']
            # Bakiye USD olduğu için doğrudan USDT miktarını kullan
            total_revenue_usd = amount_usdt * price
            
            # Bakiyeyi güncelle
            new_balance = current_balance + total_revenue_usd
            self.update_user_balance(username, new_balance)
            
            # Portföyü güncelle
            current_amount = portfolio[symbol]['amount']
            current_invested = portfolio[symbol]['total_invested']
            
            new_amount = current_amount - amount_usdt
            sold_ratio = amount_usdt / current_amount
            sold_invested = current_invested * sold_ratio
            new_invested = current_invested - sold_invested
            
            if new_amount > 0:
                new_avg_price = new_invested / new_amount
            else:
                new_avg_price = 0
            
            portfolio[symbol] = {
                'amount': new_amount,
                'avg_price': new_avg_price,
                'total_invested': new_invested
            }
            
            # Miktar 0 ise portföyden çıkar
            if new_amount <= 0:
                del portfolio[symbol]
            
            self.update_portfolio(username, portfolio)
            
            # İşlem kaydı ekle
            transaction = {
                'type': 'SELL',
                'symbol': symbol,
                'amount': amount_usdt,
                'price': price,
                'total_revenue': total_revenue_usd,
                'balance_after': new_balance
            }
            self.add_transaction(username, transaction)
            
            self.logger.info(f"{username} {amount_usdt:.6f} {symbol} sattı: ${price:.6f} (${total_revenue_usd:.2f})")
            return True
            
        except Exception as e:
            self.logger.error(f"Satma işlemi hatası: {e}")
            return False
    
    def get_portfolio_value(self, username: str, current_prices: Dict[str, float]) -> Dict:
        """Portföy değerini hesaplar"""
        portfolio = self.get_portfolio(username)
        total_value = 0.0
        total_invested = 0.0
        
        portfolio_details = {}
        
        for symbol, data in portfolio.items():
            current_price = current_prices.get(symbol, 0.0)
            amount = data['amount']
            avg_price = data['avg_price']
            invested = data['total_invested']
            
            current_value = amount * current_price
            profit_loss = current_value - invested
            profit_loss_percent = (profit_loss / invested * 100) if invested > 0 else 0
            
            total_value += current_value
            total_invested += invested
            
            portfolio_details[symbol] = {
                'amount': amount,
                'avg_price': avg_price,
                'current_price': current_price,
                'current_value': current_value,
                'invested': invested,
                'profit_loss': profit_loss,
                'profit_loss_percent': profit_loss_percent
            }
        
        cash_balance = self.get_user_balance(username)
        total_portfolio_value = total_value + cash_balance
        
        return {
            'portfolio_details': portfolio_details,
            'total_invested': total_invested,
            'total_value': total_value,
            'cash_balance': cash_balance,
            'total_portfolio_value': total_portfolio_value,
            'total_profit_loss': total_value - total_invested,
            'total_profit_loss_percent': ((total_value - total_invested) / total_invested * 100) if total_invested > 0 else 0
        } 