"""
Rapor üretimi modülü
PDF ve HTML rapor oluşturma
"""

import os
from datetime import datetime
from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
import json


class ReportGenerator:
    def __init__(self, output_dir="data/reports"):
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
        
        # Rapor stilleri
        self.styles = getSampleStyleSheet()
        self.title_style = ParagraphStyle(
            'CustomTitle',
            parent=self.styles['Heading1'],
            fontSize=16,
            spaceAfter=30,
            alignment=1  # Ortalanmış
        )
        
        self.heading_style = ParagraphStyle(
            'CustomHeading',
            parent=self.styles['Heading2'],
            fontSize=14,
            spaceAfter=12,
            spaceBefore=12
        )
        
        self.normal_style = self.styles['Normal']
    
    def create_stock_analysis_report(self, stock_data, technical_analysis, risk_analysis, 
                                   opportunity_analysis, news_sentiment, days=30):
        """
        Hisse analiz raporu oluşturur
        
        Args:
            stock_data (dict): Hisse verileri
            technical_analysis (dict): Teknik analiz
            risk_analysis (dict): Risk analizi
            opportunity_analysis (dict): Fırsat analizi
            news_sentiment (dict): Haber sentiment analizi
            days (int): Analiz edilen gün sayısı
        
        Returns:
            str: Rapor dosya yolu
        """
        filename = f"{stock_data['symbol']}_analysis_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        filepath = os.path.join(self.output_dir, filename)
        
        doc = SimpleDocTemplate(filepath, pagesize=A4)
        story = []
        
        # Başlık
        title = Paragraph(f"{stock_data['symbol']} Detaylı Analiz Raporu", self.title_style)
        story.append(title)
        
        # Tarih
        date_text = f"Rapor Tarihi: {datetime.now().strftime('%d/%m/%Y %H:%M')}"
        story.append(Paragraph(date_text, self.normal_style))
        story.append(Spacer(1, 20))
        
        # Özet Bilgiler
        story.append(Paragraph("ÖZET BİLGİLER", self.heading_style))
        
        summary_data = [
            ['Özellik', 'Değer'],
            ['Güncel Fiyat', f"{stock_data['current_price']:.2f} TL"],
            ['Günlük Değişim', f"%{stock_data['daily_change']:.2f}"],
            ['Yıllık Değişim', f"%{stock_data['yearly_change']:.2f}" if stock_data['yearly_change'] else "N/A"],
            ['Hacim', f"{stock_data['current_volume']:,.0f}"],
            ['Hacim Oranı', f"{stock_data['volume_ratio']:.2f}x"],
            ['52 Hafta Yüksek', f"{stock_data['high_52w']:.2f} TL"],
            ['52 Hafta Düşük', f"{stock_data['low_52w']:.2f} TL"]
        ]
        
        summary_table = Table(summary_data, colWidths=[2*inch, 3*inch])
        summary_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        
        story.append(summary_table)
        story.append(Spacer(1, 20))
        
        # Teknik Analiz
        if technical_analysis:
            story.append(Paragraph("TEKNİK ANALİZ", self.heading_style))
            
            tech_data = []
            if technical_analysis.get('rsi'):
                tech_data.append(['RSI', f"{technical_analysis['rsi']:.2f}"])
            if technical_analysis.get('macd'):
                tech_data.append(['MACD', f"{technical_analysis['macd']['macd']:.4f}"])
                tech_data.append(['Signal', f"{technical_analysis['macd']['signal']:.4f}"])
            if technical_analysis.get('bollinger_bands'):
                bb = technical_analysis['bollinger_bands']
                tech_data.append(['Bollinger Üst', f"{bb['upper_band']:.2f}"])
                tech_data.append(['Bollinger Alt', f"{bb['lower_band']:.2f}"])
            
            if tech_data:
                tech_table = Table(tech_data, colWidths=[2*inch, 3*inch])
                tech_table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (-1, 0), colors.lightblue),
                    ('GRID', (0, 0), (-1, -1), 1, colors.black)
                ]))
                story.append(tech_table)
                story.append(Spacer(1, 15))
        
        # Risk Analizi
        if risk_analysis:
            story.append(Paragraph("RİSK ANALİZİ", self.heading_style))
            
            risk_text = f"""
            <b>Genel Risk Seviyesi:</b> {risk_analysis['overall_risk_level']}<br/>
            <b>Risk Skoru:</b> {risk_analysis['overall_risk_score']:.1f}/100<br/>
            <b>Öneri:</b> {risk_analysis['recommendation']}<br/><br/>
            <b>Risk Faktörleri:</b><br/>
            """
            
            for factor in risk_analysis['risk_factors']:
                risk_text += f"• {factor}<br/>"
            
            story.append(Paragraph(risk_text, self.normal_style))
            story.append(Spacer(1, 15))
        
        # Fırsat Analizi
        if opportunity_analysis:
            story.append(Paragraph("FIRSAT ANALİZİ", self.heading_style))
            
            opp_text = f"""
            <b>Genel Fırsat Seviyesi:</b> {opportunity_analysis['overall_opportunity_level']}<br/>
            <b>Fırsat Skoru:</b> {opportunity_analysis['overall_opportunity_score']:.1f}/100<br/>
            <b>Öneri:</b> {opportunity_analysis['recommendation']}<br/><br/>
            <b>Fırsat Faktörleri:</b><br/>
            """
            
            for opp in opportunity_analysis['opportunities']:
                opp_text += f"• {opp}<br/>"
            
            story.append(Paragraph(opp_text, self.normal_style))
            story.append(Spacer(1, 15))
        
        # Haber Analizi
        if news_sentiment:
            story.append(Paragraph("HABER ANALİZİ", self.heading_style))
            
            news_text = f"""
            <b>Toplam Haber:</b> {news_sentiment['total_news']}<br/>
            <b>Pozitif Haber:</b> {news_sentiment['positive_news']}<br/>
            <b>Negatif Haber:</b> {news_sentiment['negative_news']}<br/>
            <b>Nötr Haber:</b> {news_sentiment['neutral_news']}<br/>
            <b>Genel Sentiment:</b> {news_sentiment['overall_sentiment']}<br/>
            <b>Sentiment Skoru:</b> {news_sentiment['sentiment_score']:.2f}<br/>
            """
            
            story.append(Paragraph(news_text, self.normal_style))
            story.append(Spacer(1, 15))
        
        # Sonuç ve Öneriler
        story.append(Paragraph("SONUÇ VE ÖNERİLER", self.heading_style))
        
        conclusion = self._generate_conclusion(stock_data, risk_analysis, opportunity_analysis)
        story.append(Paragraph(conclusion, self.normal_style))
        
        # Raporu oluştur
        doc.build(story)
        return filepath
    
    def create_watchlist_report(self, watchlist_data, days=7):
        """
        Takip listesi raporu oluşturur
        
        Args:
            watchlist_data (list): Takip listesi verileri
            days (int): Analiz edilen gün sayısı
        
        Returns:
            str: Rapor dosya yolu
        """
        filename = f"watchlist_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        filepath = os.path.join(self.output_dir, filename)
        
        doc = SimpleDocTemplate(filepath, pagesize=A4)
        story = []
        
        # Başlık
        title = Paragraph("Takip Listesi Analiz Raporu", self.title_style)
        story.append(title)
        
        # Tarih
        date_text = f"Rapor Tarihi: {datetime.now().strftime('%d/%m/%Y %H:%M')}"
        story.append(Paragraph(date_text, self.normal_style))
        story.append(Spacer(1, 20))
        
        # Takip listesi özeti
        story.append(Paragraph("TAKİP LİSTESİ ÖZETİ", self.heading_style))
        
        summary_text = f"""
        <b>Toplam Hisse Sayısı:</b> {len(watchlist_data)}<br/>
        <b>Analiz Periyodu:</b> Son {days} gün<br/>
        <b>Rapor Tarihi:</b> {datetime.now().strftime('%d/%m/%Y')}<br/>
        """
        
        story.append(Paragraph(summary_text, self.normal_style))
        story.append(Spacer(1, 15))
        
        # Hisse detayları
        if watchlist_data:
            story.append(Paragraph("HİSSE DETAYLARI", self.heading_style))
            
            # Tablo başlıkları
            table_data = [['Sembol', 'Fiyat', 'Değişim (%)', 'Hacim', 'Risk', 'Fırsat']]
            
            for stock in watchlist_data:
                risk_level = stock.get('risk_level', 'N/A')
                opportunity_level = stock.get('opportunity_level', 'N/A')
                
                table_data.append([
                    stock['symbol'],
                    f"{stock['current_price']:.2f}",
                    f"%{stock['daily_change']:.2f}",
                    f"{stock['current_volume']:,.0f}",
                    risk_level,
                    opportunity_level
                ])
            
            stock_table = Table(table_data, colWidths=[1*inch, 1*inch, 1*inch, 1.5*inch, 0.8*inch, 0.8*inch])
            stock_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 10),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('GRID', (0, 0), (-1, -1), 1, colors.black),
                ('FONTSIZE', (0, 1), (-1, -1), 8)
            ]))
            
            story.append(stock_table)
            story.append(Spacer(1, 20))
        
        # Özet istatistikler
        story.append(Paragraph("ÖZET İSTATİSTİKLER", self.heading_style))
        
        # Risk ve fırsat dağılımı
        risk_counts = {}
        opportunity_counts = {}
        
        for stock in watchlist_data:
            risk = stock.get('risk_level', 'N/A')
            opportunity = stock.get('opportunity_level', 'N/A')
            
            risk_counts[risk] = risk_counts.get(risk, 0) + 1
            opportunity_counts[opportunity] = opportunity_counts.get(opportunity, 0) + 1
        
        stats_text = "<b>Risk Dağılımı:</b><br/>"
        for risk, count in risk_counts.items():
            stats_text += f"• {risk}: {count} hisse<br/>"
        
        stats_text += "<br/><b>Fırsat Dağılımı:</b><br/>"
        for opp, count in opportunity_counts.items():
            stats_text += f"• {opp}: {count} hisse<br/>"
        
        story.append(Paragraph(stats_text, self.normal_style))
        
        # Raporu oluştur
        doc.build(story)
        return filepath
    
    def create_market_summary_report(self, market_data, top_gainers, top_losers, days=1):
        """
        Piyasa özet raporu oluşturur
        
        Args:
            market_data (dict): Piyasa verileri
            top_gainers (list): En çok yükselen hisseler
            top_losers (list): En çok düşen hisseler
            days (int): Analiz edilen gün sayısı
        
        Returns:
            str: Rapor dosya yolu
        """
        filename = f"market_summary_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        filepath = os.path.join(self.output_dir, filename)
        
        doc = SimpleDocTemplate(filepath, pagesize=A4)
        story = []
        
        # Başlık
        title = Paragraph("Piyasa Özet Raporu", self.title_style)
        story.append(title)
        
        # Tarih
        date_text = f"Rapor Tarihi: {datetime.now().strftime('%d/%m/%Y %H:%M')}"
        story.append(Paragraph(date_text, self.normal_style))
        story.append(Spacer(1, 20))
        
        # Piyasa özeti
        story.append(Paragraph("PİYASA ÖZETİ", self.heading_style))
        
        if market_data:
            market_text = f"""
            <b>BIST-100 Endeksi:</b> {market_data.get('bist100', 'N/A')}<br/>
            <b>Günlük Değişim:</b> {market_data.get('daily_change', 'N/A')}<br/>
            <b>Toplam İşlem Hacmi:</b> {market_data.get('total_volume', 'N/A')}<br/>
            <b>İşlem Gören Hisse Sayısı:</b> {market_data.get('active_stocks', 'N/A')}<br/>
            """
            story.append(Paragraph(market_text, self.normal_style))
            story.append(Spacer(1, 15))
        
        # En çok yükselen hisseler
        if top_gainers:
            story.append(Paragraph("EN ÇOK YÜKSELEN HİSSELER", self.heading_style))
            
            gainer_data = [['Sembol', 'Fiyat', 'Değişim (%)', 'Hacim']]
            for stock in top_gainers[:10]:  # İlk 10
                gainer_data.append([
                    stock['symbol'],
                    f"{stock['current_price']:.2f}",
                    f"%{stock['daily_change']:.2f}",
                    f"{stock['current_volume']:,.0f}"
                ])
            
            gainer_table = Table(gainer_data, colWidths=[1.5*inch, 1.5*inch, 1.5*inch, 2*inch])
            gainer_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.green),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            
            story.append(gainer_table)
            story.append(Spacer(1, 15))
        
        # En çok düşen hisseler
        if top_losers:
            story.append(Paragraph("EN ÇOK DÜŞEN HİSSELER", self.heading_style))
            
            loser_data = [['Sembol', 'Fiyat', 'Değişim (%)', 'Hacim']]
            for stock in top_losers[:10]:  # İlk 10
                loser_data.append([
                    stock['symbol'],
                    f"{stock['current_price']:.2f}",
                    f"%{stock['daily_change']:.2f}",
                    f"{stock['current_volume']:,.0f}"
                ])
            
            loser_table = Table(loser_data, colWidths=[1.5*inch, 1.5*inch, 1.5*inch, 2*inch])
            loser_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.red),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            
            story.append(loser_table)
        
        # Raporu oluştur
        doc.build(story)
        return filepath
    
    def _generate_conclusion(self, stock_data, risk_analysis, opportunity_analysis):
        """
        Sonuç ve öneriler metni oluşturur
        
        Args:
            stock_data (dict): Hisse verileri
            risk_analysis (dict): Risk analizi
            opportunity_analysis (dict): Fırsat analizi
        
        Returns:
            str: Sonuç metni
        """
        conclusion = "<b>SONUÇ VE ÖNERİLER:</b><br/><br/>"
        
        # Risk değerlendirmesi
        if risk_analysis:
            if risk_analysis['overall_risk_level'] == "YÜKSEK":
                conclusion += "⚠️ <b>Yüksek Risk:</b> Bu hisse yüksek risk taşımaktadır. "
                conclusion += "Yatırım yapmadan önce dikkatli değerlendirme yapılmalıdır.<br/><br/>"
            elif risk_analysis['overall_risk_level'] == "ORTA":
                conclusion += "⚠️ <b>Orta Risk:</b> Bu hisse orta seviyede risk taşımaktadır. "
                conclusion += "Risk yönetimi kurallarına uygun hareket edilmelidir.<br/><br/>"
            else:
                conclusion += "✅ <b>Düşük Risk:</b> Bu hisse düşük risk seviyesindedir. "
                conclusion += "Göreceli olarak güvenli bir yatırım seçeneği olabilir.<br/><br/>"
        
        # Fırsat değerlendirmesi
        if opportunity_analysis:
            if opportunity_analysis['overall_opportunity_level'] == "YÜKSEK":
                conclusion += "🚀 <b>Yüksek Fırsat:</b> Bu hisse güçlü alım fırsatları sunmaktadır. "
                conclusion += "Teknik ve temel analizler olumlu sinyaller vermektedir.<br/><br/>"
            elif opportunity_analysis['overall_opportunity_level'] == "ORTA":
                conclusion += "📈 <b>Orta Fırsat:</b> Bu hisse orta seviyede fırsatlar sunmaktadır. "
                conclusion += "Takip edilmesi ve uygun zamanlarda değerlendirilmesi önerilir.<br/><br/>"
            else:
                conclusion += "⏳ <b>Düşük Fırsat:</b> Bu hisse şu anda düşük fırsat seviyesindedir. "
                conclusion += "Daha iyi fırsatlar için beklenebilir.<br/><br/>"
        
        # Genel öneri
        conclusion += "<b>GENEL ÖNERİ:</b><br/>"
        
        if risk_analysis and opportunity_analysis:
            risk_score = risk_analysis['overall_risk_score']
            opp_score = opportunity_analysis['overall_opportunity_score']
            
            if opp_score > 50 and risk_score < 40:
                conclusion += "✅ <b>GÜÇLÜ ALIM:</b> Düşük risk, yüksek fırsat profili. "
                conclusion += "Yatırım için uygun görünmektedir."
            elif opp_score > 30 and risk_score < 60:
                conclusion += "📊 <b>TAKİP ET:</b> Orta seviye fırsat ve risk. "
                conclusion += "Düzenli takip edilmesi önerilir."
            elif risk_score > 60:
                conclusion += "⚠️ <b>DİKKAT:</b> Yüksek risk profili. "
                conclusion += "Yatırım yapmadan önce detaylı analiz gerekir."
            else:
                conclusion += "⏸️ <b>BEKLE:</b> Şu anda net bir sinyal yok. "
                conclusion += "Piyasa koşulları değişene kadar beklenebilir."
        
        conclusion += "<br/><br/><b>NOT:</b> Bu rapor sadece bilgilendirme amaçlıdır. "
        conclusion += "Yatırım kararları kişisel sorumluluğunuzdadır."
        
        return conclusion
    
    def create_html_report(self, stock_data, technical_analysis, risk_analysis, 
                          opportunity_analysis, news_sentiment, days=30):
        """
        HTML formatında rapor oluşturur
        """
        filename = f"{stock_data['symbol']}_analysis_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
        filepath = os.path.join(self.output_dir, filename)

        # Yıllık değişim stringini hazırla
        yearly_change = stock_data.get('yearly_change')
        if yearly_change is not None:
            yearly_change_str = f"%{yearly_change:.2f}"
        else:
            yearly_change_str = "N/A"

        html_content = f"""
        <!DOCTYPE html>
        <html lang="tr">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>{stock_data['symbol']} Analiz Raporu</title>
            <style>
                body {{ font-family: Arial, sans-serif; margin: 20px; }}
                .header {{ text-align: center; margin-bottom: 30px; }}
                .section {{ margin-bottom: 25px; }}
                .section h2 {{ color: #2c3e50; border-bottom: 2px solid #3498db; padding-bottom: 5px; }}
                .summary-table {{ width: 100%; border-collapse: collapse; margin: 15px 0; }}
                .summary-table th, .summary-table td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
                .summary-table th {{ background-color: #f2f2f2; font-weight: bold; }}
                .risk-high {{ color: #e74c3c; font-weight: bold; }}
                .risk-medium {{ color: #f39c12; font-weight: bold; }}
                .risk-low {{ color: #27ae60; font-weight: bold; }}
                .opportunity-high {{ color: #27ae60; font-weight: bold; }}
                .opportunity-medium {{ color: #f39c12; font-weight: bold; }}
                .opportunity-low {{ color: #e74c3c; font-weight: bold; }}
            </style>
        </head>
        <body>
            <div class="header">
                <h1>{stock_data['symbol']} Detaylı Analiz Raporu</h1>
                <p>Rapor Tarihi: {datetime.now().strftime('%d/%m/%Y %H:%M')}</p>
            </div>
            
            <div class="section">
                <h2>ÖZET BİLGİLER</h2>
                <table class="summary-table">
                    <tr><th>Özellik</th><th>Değer</th></tr>
                    <tr><td>Güncel Fiyat</td><td>{stock_data['current_price']:.2f} TL</td></tr>
                    <tr><td>Günlük Değişim</td><td>%{stock_data['daily_change']:.2f}</td></tr>
                    <tr><td>Yıllık Değişim</td><td>{yearly_change_str}</td></tr>
                    <tr><td>Hacim</td><td>{stock_data['current_volume']:,.0f}</td></tr>
                    <tr><td>Hacim Oranı</td><td>{stock_data['volume_ratio']:.2f}x</td></tr>
                </table>
            </div>
        """
        
        # Risk analizi
        if risk_analysis:
            risk_class = f"risk-{risk_analysis['overall_risk_level'].lower()}"
            html_content += f"""
            <div class="section">
                <h2>RİSK ANALİZİ</h2>
                <p><strong>Genel Risk Seviyesi:</strong> <span class="{risk_class}">{risk_analysis['overall_risk_level']}</span></p>
                <p><strong>Risk Skoru:</strong> {risk_analysis['overall_risk_score']:.1f}/100</p>
                <p><strong>Öneri:</strong> {risk_analysis['recommendation']}</p>
                <h3>Risk Faktörleri:</h3>
                <ul>
            """
            for factor in risk_analysis['risk_factors']:
                html_content += f"<li>{factor}</li>"
            html_content += "</ul></div>"
        
        # Fırsat analizi
        if opportunity_analysis:
            opp_class = f"opportunity-{opportunity_analysis['overall_opportunity_level'].lower()}"
            html_content += f"""
            <div class="section">
                <h2>FIRSAT ANALİZİ</h2>
                <p><strong>Genel Fırsat Seviyesi:</strong> <span class="{opp_class}">{opportunity_analysis['overall_opportunity_level']}</span></p>
                <p><strong>Fırsat Skoru:</strong> {opportunity_analysis['overall_opportunity_score']:.1f}/100</p>
                <p><strong>Öneri:</strong> {opportunity_analysis['recommendation']}</p>
                <h3>Fırsat Faktörleri:</h3>
                <ul>
            """
            for opp in opportunity_analysis['opportunities']:
                html_content += f"<li>{opp}</li>"
            html_content += "</ul></div>"
        
        html_content += """
        </body>
        </html>
        """
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        return filepath 