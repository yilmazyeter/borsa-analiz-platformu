"""
Grafik üretimi modülü
Matplotlib ve Plotly ile grafik oluşturma
"""

import matplotlib.pyplot as plt
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np
from datetime import datetime
import os


class ChartGenerator:
    def __init__(self, output_dir="data/charts"):
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
        
        # Matplotlib Türkçe karakter desteği
        plt.rcParams['font.family'] = ['DejaVu Sans']
    
    def create_price_chart(self, stock_data, save_path=None):
        """
        Fiyat grafiği oluşturur
        
        Args:
            stock_data (dict): Hisse verileri
            save_path (str): Kaydetme yolu
        
        Returns:
            str: Grafik dosya yolu
        """
        if 'historical_data' not in stock_data or not stock_data['historical_data']:
            return None
            
        df = pd.DataFrame(stock_data['historical_data'])
        df['Date'] = pd.to_datetime(df['Date'])
        
        # Plotly ile candlestick grafik
        fig = go.Figure()
        
        fig.add_trace(go.Candlestick(
            x=df['Date'],
            open=df['Open'],
            high=df['High'],
            low=df['Low'],
            close=df['Close'],
            name='Fiyat'
        ))
        
        # Hareketli ortalamalar
        df['MA5'] = df['Close'].rolling(window=5).mean()
        df['MA20'] = df['Close'].rolling(window=20).mean()
        
        fig.add_trace(go.Scatter(
            x=df['Date'],
            y=df['MA5'],
            mode='lines',
            name='MA5',
            line=dict(color='orange', width=1)
        ))
        
        fig.add_trace(go.Scatter(
            x=df['Date'],
            y=df['MA20'],
            mode='lines',
            name='MA20',
            line=dict(color='blue', width=1)
        ))
        
        fig.update_layout(
            title=f"{stock_data['symbol']} Fiyat Grafiği",
            xaxis_title="Tarih",
            yaxis_title="Fiyat (TL)",
            template="plotly_white"
        )
        
        if save_path is None:
            save_path = os.path.join(self.output_dir, f"{stock_data['symbol']}_price_chart.html")
        
        fig.write_html(save_path)
        return save_path
    
    def create_volume_chart(self, stock_data, save_path=None):
        """
        Hacim grafiği oluşturur
        
        Args:
            stock_data (dict): Hisse verileri
            save_path (str): Kaydetme yolu
        
        Returns:
            str: Grafik dosya yolu
        """
        if 'historical_data' not in stock_data:
            return None
            
        df = pd.DataFrame(stock_data['historical_data'])
        df['Date'] = pd.to_datetime(df.index)
        
        fig = go.Figure()
        
        fig.add_trace(go.Bar(
            x=df['Date'],
            y=df['Volume'],
            name='Hacim',
            marker_color='lightblue'
        ))
        
        # Ortalama hacim çizgisi
        avg_volume = df['Volume'].mean()
        fig.add_hline(y=avg_volume, line_dash="dash", line_color="red",
                     annotation_text=f"Ortalama: {avg_volume:,.0f}")
        
        fig.update_layout(
            title=f"{stock_data['symbol']} Hacim Grafiği",
            xaxis_title="Tarih",
            yaxis_title="Hacim",
            template="plotly_white"
        )
        
        if save_path is None:
            save_path = os.path.join(self.output_dir, f"{stock_data['symbol']}_volume_chart.html")
        
        fig.write_html(save_path)
        return save_path
    
    def create_technical_indicators_chart(self, stock_data, technical_analysis, save_path=None):
        """
        Teknik göstergeler grafiği oluşturur
        
        Args:
            stock_data (dict): Hisse verileri
            technical_analysis (dict): Teknik analiz sonuçları
            save_path (str): Kaydetme yolu
        
        Returns:
            str: Grafik dosya yolu
        """
        if 'historical_data' not in stock_data:
            return None
            
        df = pd.DataFrame(stock_data['historical_data'])
        df['Date'] = pd.to_datetime(df.index)
        
        # Alt grafikler oluştur
        fig = make_subplots(
            rows=3, cols=1,
            subplot_titles=('Fiyat ve Bollinger Bantları', 'RSI', 'MACD'),
            vertical_spacing=0.1
        )
        
        # Fiyat ve Bollinger Bantları
        fig.add_trace(go.Scatter(
            x=df['Date'],
            y=df['Close'],
            mode='lines',
            name='Fiyat',
            line=dict(color='black')
        ), row=1, col=1)
        
        if technical_analysis and technical_analysis.get('bollinger_bands'):
            bb = technical_analysis['bollinger_bands']
            # Basit Bollinger Bantları (gerçek uygulamada hesaplanmalı)
            df['BB_Upper'] = df['Close'].rolling(window=20).mean() + 2 * df['Close'].rolling(window=20).std()
            df['BB_Lower'] = df['Close'].rolling(window=20).mean() - 2 * df['Close'].rolling(window=20).std()
            
            fig.add_trace(go.Scatter(
                x=df['Date'],
                y=df['BB_Upper'],
                mode='lines',
                name='Üst Band',
                line=dict(color='gray', dash='dash')
            ), row=1, col=1)
            
            fig.add_trace(go.Scatter(
                x=df['Date'],
                y=df['BB_Lower'],
                mode='lines',
                name='Alt Band',
                line=dict(color='gray', dash='dash')
            ), row=1, col=1)
        
        # RSI
        if technical_analysis and technical_analysis.get('rsi'):
            # Basit RSI hesaplama
            delta = df['Close'].diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
            rs = gain / loss
            df['RSI'] = 100 - (100 / (1 + rs))
            
            fig.add_trace(go.Scatter(
                x=df['Date'],
                y=df['RSI'],
                mode='lines',
                name='RSI',
                line=dict(color='purple')
            ), row=2, col=1)
            
            # RSI seviyeleri
            fig.add_hline(y=70, line_dash="dash", line_color="red", row=2, col=1)
            fig.add_hline(y=30, line_dash="dash", line_color="green", row=2, col=1)
        
        # MACD
        if technical_analysis and technical_analysis.get('macd'):
            # Basit MACD hesaplama
            df['EMA12'] = df['Close'].ewm(span=12).mean()
            df['EMA26'] = df['Close'].ewm(span=26).mean()
            df['MACD'] = df['EMA12'] - df['EMA26']
            df['Signal'] = df['MACD'].ewm(span=9).mean()
            
            fig.add_trace(go.Scatter(
                x=df['Date'],
                y=df['MACD'],
                mode='lines',
                name='MACD',
                line=dict(color='blue')
            ), row=3, col=1)
            
            fig.add_trace(go.Scatter(
                x=df['Date'],
                y=df['Signal'],
                mode='lines',
                name='Signal',
                line=dict(color='red')
            ), row=3, col=1)
        
        fig.update_layout(
            title=f"{stock_data['symbol']} Teknik Göstergeler",
            height=800,
            template="plotly_white"
        )
        
        if save_path is None:
            save_path = os.path.join(self.output_dir, f"{stock_data['symbol']}_technical_chart.html")
        
        fig.write_html(save_path)
        return save_path
    
    def create_sentiment_chart(self, news_sentiment, save_path=None):
        """
        Sentiment analizi grafiği oluşturur
        
        Args:
            news_sentiment (dict): Haber sentiment analizi
            save_path (str): Kaydetme yolu
        
        Returns:
            str: Grafik dosya yolu
        """
        if not news_sentiment:
            return None
        
        # Sentiment dağılımı
        sentiment_data = {
            'Pozitif': news_sentiment['positive_news'],
            'Negatif': news_sentiment['negative_news'],
            'Nötr': news_sentiment['neutral_news']
        }
        
        fig = go.Figure(data=[go.Pie(
            labels=list(sentiment_data.keys()),
            values=list(sentiment_data.values()),
            hole=0.3
        )])
        
        fig.update_layout(
            title=f"{news_sentiment['symbol']} Haber Sentiment Analizi",
            template="plotly_white"
        )
        
        if save_path is None:
            save_path = os.path.join(self.output_dir, f"{news_sentiment['symbol']}_sentiment_chart.html")
        
        fig.write_html(save_path)
        return save_path
    
    def create_comparison_chart(self, stocks_data, save_path=None):
        """
        Birden fazla hisse karşılaştırma grafiği
        
        Args:
            stocks_data (list): Hisse verileri listesi
            save_path (str): Kaydetme yolu
        
        Returns:
            str: Grafik dosya yolu
        """
        fig = go.Figure()
        
        for stock_data in stocks_data:
            if 'historical_data' in stock_data:
                df = pd.DataFrame(stock_data['historical_data'])
                df['Date'] = pd.to_datetime(df.index)
                
                # Normalize edilmiş fiyat (ilk gün = 100)
                first_price = df['Close'].iloc[0]
                df['Normalized_Price'] = (df['Close'] / first_price) * 100
                
                fig.add_trace(go.Scatter(
                    x=df['Date'],
                    y=df['Normalized_Price'],
                    mode='lines',
                    name=stock_data['symbol'],
                    line=dict(width=2)
                ))
        
        fig.update_layout(
            title="Hisse Karşılaştırma Grafiği (Normalize Edilmiş)",
            xaxis_title="Tarih",
            yaxis_title="Normalize Edilmiş Fiyat (İlk gün = 100)",
            template="plotly_white"
        )
        
        if save_path is None:
            save_path = os.path.join(self.output_dir, "stock_comparison_chart.html")
        
        fig.write_html(save_path)
        return save_path
    
    def create_matplotlib_chart(self, stock_data, save_path=None):
        """
        Matplotlib ile basit grafik oluşturur
        
        Args:
            stock_data (dict): Hisse verileri
            save_path (str): Kaydetme yolu
        
        Returns:
            str: Grafik dosya yolu
        """
        if 'historical_data' not in stock_data:
            return None
            
        df = pd.DataFrame(stock_data['historical_data'])
        
        plt.figure(figsize=(12, 8))
        
        # Fiyat grafiği
        plt.subplot(2, 1, 1)
        plt.plot(df.index, df['Close'], label='Kapanış Fiyatı', linewidth=2)
        plt.title(f"{stock_data['symbol']} Fiyat Grafiği")
        plt.ylabel('Fiyat (TL)')
        plt.legend()
        plt.grid(True)
        
        # Hacim grafiği
        plt.subplot(2, 1, 2)
        plt.bar(df.index, df['Volume'], alpha=0.7, color='lightblue')
        plt.title(f"{stock_data['symbol']} Hacim Grafiği")
        plt.ylabel('Hacim')
        plt.xlabel('Tarih')
        plt.grid(True)
        
        plt.tight_layout()
        
        if save_path is None:
            save_path = os.path.join(self.output_dir, f"{stock_data['symbol']}_matplotlib_chart.png")
        
        plt.savefig(save_path, dpi=300, bbox_inches='tight')
        plt.close()
        
        return save_path 