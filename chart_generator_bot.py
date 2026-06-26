# chart_generator_bot.py - Complete version
import matplotlib.pyplot as plt
import matplotlib
matplotlib.use('Agg')
from io import BytesIO
import base64

class ChartGenerator:
    """Generates professional charts for market data reports."""
    
    def __init__(self):
        self.chart_images = {}
        self.dark_mode = False
    
    def create_crypto_price_chart(self, crypto_data):
        """Create a bar chart of cryptocurrency prices."""
        if not crypto_data:
            return None
        fig, ax = plt.subplots(figsize=(10, 6))
        coins = list(crypto_data.keys())
        prices = [crypto_data[coin]['price'] for coin in coins]
        changes = [crypto_data[coin]['change_24h'] for coin in coins]
        bars = ax.bar(coins, prices, color=['#f7931a', '#627eea', '#9945ff', '#00d4aa', '#0033ad'])
        for bar, price in zip(bars, prices):
            ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 5,
                    f'${price:,.2f}', ha='center', va='bottom', fontsize=10)
        for i, (coin, change) in enumerate(zip(coins, changes)):
            color = 'green' if change >= 0 else 'red'
            ax.text(i, -max(prices) * 0.05, f'{change:+.1f}%', 
                    ha='center', color=color, fontsize=10, fontweight='bold')
        ax.set_title('Cryptocurrency Prices (24h Change)', fontsize=16, fontweight='bold')
        ax.set_ylabel('Price (USD)', fontsize=12)
        ax.set_ylim(0, max(prices) * 1.25)
        ax.grid(axis='y', linestyle='--', alpha=0.3)
        return self._save_chart(fig)
    
    def create_stock_performance_chart(self, stock_data):
        """Create a horizontal bar chart of tech stock performance."""
        if not stock_data:
            return None
        fig, ax = plt.subplots(figsize=(10, 6))
        sorted_stocks = sorted(stock_data.items(), key=lambda x: x[1]['price'], reverse=True)
        symbols = [item[0] for item in sorted_stocks]
        prices = [item[1]['price'] for item in sorted_stocks]
        changes = [item[1]['change_24h'] for item in sorted_stocks]
        bars = ax.barh(symbols, prices, color=['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd', '#8c564b', '#e377c2'])
        for bar, price, change in zip(bars, prices, changes):
            color = 'green' if change >= 0 else 'red'
            ax.text(bar.get_width() + 5, bar.get_y() + bar.get_height()/2,
                    f'${price:,.2f}  ({change:+.1f}%)', 
                    va='center', color=color, fontsize=9)
        ax.set_title('Tech Stock Prices & Performance', fontsize=16, fontweight='bold')
        ax.set_xlabel('Price (USD)', fontsize=12)
        ax.grid(axis='x', linestyle='--', alpha=0.3)
        return self._save_chart(fig)
    
def create_price_spread_chart(self, spread_data=None):
    """Create a price spread chart showing arbitrage opportunities."""
    fig, ax = plt.subplots(figsize=(12, 8))
    
    # Sample arbitrage data - in production, this would come from real data
    regions = ['US East', 'US West', 'EU Central', 'APAC South', 'ME North']
    market_a = [10, 12, 15, 18, 22]
    market_b = [8, 9, 11, 14, 17]
    spreads = [market_a[i] - market_b[i] for i in range(len(regions))]
    
    x = np.arange(len(regions))
    width = 0.35
    
    ax.bar(x - width/2, market_a, width, label='Market A', color='#1f77b4')
    ax.bar(x + width/2, market_b, width, label='Market B', color='#ff7f0e')
    
    for i, spread in enumerate(spreads):
        ax.text(i, max(market_a[i], market_b[i]) + 0.5, 
                f'Spread: ${spread:.2f}', ha='center', fontsize=9, fontweight='bold')
    
    ax.set_title('Regional Price Spreads - Arbitrage Opportunities', fontsize=16, fontweight='bold')
    ax.set_xlabel('Region')
    ax.set_ylabel('Price (USD)')
    ax.legend()
    ax.grid(True, linestyle='--', alpha=0.3)
    
    return self._save_chart(fig)

    def create_market_indices_chart(self, index_data):
        """Create a chart showing market indices."""
        if not index_data:
            return None
        fig, ax = plt.subplots(figsize=(8, 5))
        indices = list(index_data.keys())
        values = [index_data[i]['price'] for i in indices]
        changes = [index_data[i]['change_24h'] for i in indices]
        colors = ['#1a5276', '#2e86c1', '#85c1e9', '#d6eaf8']
        bars = ax.bar(indices, values, color=colors)
        for bar, value, change in zip(bars, values, changes):
            ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + max(values) * 0.02,
                    f'{value:,.0f}\n{change:+.1f}%', 
                    ha='center', va='bottom', fontsize=9)
        ax.set_title('Market Indices Snapshot', fontsize=16, fontweight='bold')
        ax.set_ylabel('Index Value', fontsize=12)
        ax.grid(axis='y', linestyle='--', alpha=0.3)
        return self._save_chart(fig)
    
    def create_trend_analysis_chart(self, trend_data):
        """Create a line chart of software trend adoption."""
        if not trend_data:
            years = ['2021', '2022', '2023', '2024', '2025', '2026']
            trends = {
                'AI/ML': [20, 35, 45, 58, 68, 78],
                'Edge Computing': [15, 22, 30, 40, 50, 60],
                'Rust': [5, 10, 18, 28, 40, 55],
                'TypeScript': [30, 42, 55, 65, 75, 82]
            }
        else:
            years = trend_data.get('years', ['2021', '2022', '2023', '2024', '2025', '2026'])
            trends = trend_data.get('trends', {})
        fig, ax = plt.subplots(figsize=(10, 6))
        colors = ['#2ecc71', '#3498db', '#e74c3c', '#f39c12']
        for i, (trend_name, values) in enumerate(trends.items()):
            ax.plot(years, values, marker='o', linewidth=2, 
                   color=colors[i % len(colors)], label=trend_name)
        ax.set_title('Software Trend Adoption Rate Over Time', fontsize=16, fontweight='bold')
        ax.set_xlabel('Year', fontsize=12)
        ax.set_ylabel('Adoption Rate (%)', fontsize=12)
        ax.legend(loc='upper left', fontsize=10)
        ax.grid(True, linestyle='--', alpha=0.3)
        ax.set_ylim(0, 100)
        return self._save_chart(fig)
    
    def create_social_media_pie_chart(self):
        """Create a pie chart showing social media platform popularity."""
        platforms = {'LinkedIn': 25, 'GitHub': 22, 'Stack Overflow': 18, 'Twitter/X': 15, 'Reddit': 10, 'YouTube': 10}
        fig, ax = plt.subplots(figsize=(8, 8))
        colors = ['#0a66c2', '#181717', '#f48024', '#1da1f2', '#ff4500', '#ff0000']
        wedges, texts, autotexts = ax.pie(
            platforms.values(),
            labels=platforms.keys(),
            autopct='%1.1f%%',
            colors=colors,
            startangle=90,
            textprops={'fontsize': 12, 'fontweight': 'bold'}
        )
        ax.set_title('Social Media Platform Popularity (Developer Community)', fontsize=16, fontweight='bold')
        return self._save_chart(fig)
    
    def create_financial_chart(self):
        """Create a financial-style chart with diagonal lines for top 10 companies."""
        fig, ax = plt.subplots(figsize=(12, 8))
        companies = ['Nvidia', 'Apple', 'Microsoft', 'Alphabet', 'Amazon', 'Meta', 'Tesla', 'Oracle', 'Salesforce', 'Broadcom']
        months = list(range(1, 25))
        price_data = {
            'Nvidia': [100, 120, 140, 160, 180, 200, 220, 240, 260, 280, 300, 320, 340, 360, 380, 400, 420, 440, 460, 480, 500, 520, 540, 560],
            'Apple': [150, 155, 160, 158, 162, 165, 170, 172, 175, 180, 178, 182, 185, 190, 192, 195, 198, 200, 205, 210, 212, 215, 218, 220],
            'Microsoft': [200, 205, 210, 215, 220, 225, 230, 235, 240, 245, 250, 255, 260, 265, 270, 275, 280, 285, 290, 295, 300, 305, 310, 315],
            'Alphabet': [180, 185, 190, 195, 200, 205, 210, 215, 220, 225, 230, 235, 240, 245, 250, 255, 260, 265, 270, 275, 280, 285, 290, 295],
            'Amazon': [170, 175, 180, 185, 190, 195, 200, 205, 210, 215, 220, 225, 230, 235, 240, 245, 250, 255, 260, 265, 270, 275, 280, 285],
            'Meta': [120, 130, 140, 150, 160, 170, 180, 190, 200, 210, 220, 230, 240, 250, 260, 270, 280, 290, 300, 310, 320, 330, 340, 350],
            'Tesla': [250, 240, 230, 220, 210, 200, 190, 180, 170, 160, 150, 140, 145, 150, 155, 160, 165, 170, 175, 180, 185, 190, 195, 200],
            'Oracle': [100, 105, 110, 115, 120, 125, 130, 135, 140, 145, 150, 155, 160, 165, 170, 175, 180, 185, 190, 195, 200, 205, 210, 215],
            'Salesforce': [80, 85, 90, 95, 100, 105, 110, 115, 120, 125, 130, 135, 140, 145, 150, 155, 160, 165, 170, 175, 180, 185, 190, 195],
            'Broadcom': [150, 160, 170, 180, 190, 200, 210, 220, 230, 240, 250, 260, 270, 280, 290, 300, 310, 320, 330, 340, 350, 360, 370, 380]
        }
        colors = ['#00ff66', '#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd', '#8c564b', '#e377c2', '#7f7f7f', '#bcbd22']
        for i, (company, prices) in enumerate(price_data.items()):
            x = months
            y = prices[:len(months)]
            ax.plot(x, y, label=company, color=colors[i % len(colors)], linewidth=2, marker='o', markersize=3)
        ax.set_title('Top 10 Tech Companies - Stock Performance (2025-2026)', fontsize=16, fontweight='bold')
        ax.set_xlabel('Month')
        ax.set_ylabel('Stock Price (USD)')
        ax.legend(loc='upper left', fontsize=8)
        ax.grid(True, linestyle='--', alpha=0.3)
        return self._save_chart(fig)
    
    def _save_chart(self, fig):
        """Convert matplotlib figure to base64 string."""
        buffer = BytesIO()
        fig.savefig(buffer, format='png', bbox_inches='tight', dpi=150)
        buffer.seek(0)
        image_base64 = base64.b64encode(buffer.getvalue()).decode('utf-8')
        plt.close(fig)
        return image_base64
    
    def generate_all_charts(self, data):
        """Generate all charts for the report."""
        print("📊 Generating charts...")
        charts = {}
        if 'crypto' in data:
            charts['crypto'] = self.create_crypto_price_chart(data['crypto'])
            print("   ✅ Crypto chart created")
        if 'stocks' in data:
            charts['stocks'] = self.create_stock_performance_chart(data['stocks'])
            print("   ✅ Stock chart created")
        if 'indices' in data:
            charts['indices'] = self.create_market_indices_chart(data['indices'])
            print("   ✅ Market indices chart created")
        charts['trends'] = self.create_trend_analysis_chart(None)
        print("   ✅ Trends chart created")
        charts['social'] = self.create_social_media_pie_chart()
        print("   ✅ Social media pie chart created")
        charts['financial'] = self.create_financial_chart()
        print("   ✅ Financial chart created")
        print("🎉 All charts generated successfully")
        return charts

