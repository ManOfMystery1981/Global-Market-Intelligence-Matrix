# Add this function to chart_generator_bot.py
def create_financial_chart(self):
    """Create a financial-style chart with diagonal lines for top 10 companies."""
    fig, ax = plt.subplots(figsize=(12, 8))
    
    # Sample data for top 10 companies over 2 years
    companies = ['Nvidia', 'Apple', 'Microsoft', 'Alphabet', 'Amazon', 
                 'Meta', 'Tesla', 'Oracle', 'Salesforce', 'Broadcom']
    
    # Simulated price data over 24 months (2025-2026)
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
    
    colors = ['#00ff66', '#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', 
              '#9467bd', '#8c564b', '#e377c2', '#7f7f7f', '#bcbd22']
    
    for i, (company, prices) in enumerate(price_data.items()):
        # Create the diagonal jagged line
        x = months
        y = prices[:len(months)]
        
        # Plot the line
        ax.plot(x, y, label=company, color=colors[i % len(colors)], 
                linewidth=2, marker='o', markersize=3)
    
    ax.set_title('Top 10 Tech Companies - Stock Performance (2025-2026)', 
                 fontsize=16, fontweight='bold')
    ax.set_xlabel('Month')
    ax.set_ylabel('Stock Price (USD)')
    ax.legend(loc='upper left', fontsize=8)
    ax.grid(True, linestyle='--', alpha=0.3)
    
    return self._save_chart(fig)
