# Crypto Portfolio Tracker

Advanced cryptocurrency portfolio management and analysis tool with real-time data, technical analysis, and AI-powered insights.

## 🚀 Deploy Options

### Option 1: Streamlit Cloud (Recommended)

1. **Fork this repository** to your GitHub account
2. **Go to [share.streamlit.io](https://share.streamlit.io)**
3. **Connect your GitHub account**
4. **Select this repository**
5. **Set the main file path:** `web_app_backup.py`
6. **Click Deploy**

### Option 2: Heroku

1. **Install Heroku CLI:**
   ```bash
   # Windows
   winget install --id=Heroku.HerokuCLI
   
   # macOS
   brew tap heroku/brew && brew install heroku
   ```

2. **Login to Heroku:**
   ```bash
   heroku login
   ```

3. **Create Heroku app:**
   ```bash
   heroku create your-app-name
   ```

4. **Deploy:**
   ```bash
   git push heroku main
   ```

5. **Open the app:**
   ```bash
   heroku open
   ```

### Option 3: Local Development

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Run the app:**
   ```bash
   streamlit run web_app_backup.py
   ```

## 📊 Features

- **Real-time Crypto Data:** Live prices from Binance API
- **Portfolio Management:** Track your crypto investments
- **Technical Analysis:** RSI, Bollinger Bands, MACD
- **AI-Powered Insights:** Opportunity detection and recommendations
- **Whale Analysis:** Track large investor movements
- **1-Hour Profit Analysis:** Short-term trading opportunities
- **Price Recommendations:** Entry and exit price suggestions
- **Auto-refresh:** Live updates every 5 seconds

## 🔧 Configuration

The app uses the following configuration files:
- `.streamlit/config.toml` - Streamlit settings
- `requirements.txt` - Python dependencies
- `Procfile` - Heroku deployment
- `setup.sh` - Deployment setup script

## 📈 Screenshots

- Portfolio tracking with real-time profit/loss
- Technical analysis with price recommendations
- Whale activity analysis
- 1-hour profit opportunity detection

## 🛠️ Tech Stack

- **Frontend:** Streamlit
- **Backend:** Python 3.11
- **Data:** Binance API, Pandas, NumPy
- **Analysis:** Scikit-learn, Technical indicators
- **Deployment:** Streamlit Cloud / Heroku

## 📝 License

MIT License - feel free to use and modify! 