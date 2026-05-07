import streamlit as st
import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt
import datetime

# 1. 共通設定（英語表記で固定）
symbol_map = {
    '6255.T': 'NPC',
    '464A.T': 'QPS Institute',
    '3778.T': 'Sakura Internet'
}
symbols = list(symbol_map.keys())

# --- 共通データ取得関数 ---
@st.cache_data(ttl=300)
def get_data(ticker):
    data = yf.download(ticker, period="150d", auto_adjust=True)
    if isinstance(data.columns, pd.MultiIndex):
        data.columns = data.columns.get_level_values(0)
    data = data.dropna(subset=['Close'])
    data['MA25'] = data['Close'].rolling(window=25).mean()
    data['Kairi'] = ((data['Close'] - data['MA25']) / data['MA25']) * 100
    return data

# 2. サイドバー
with st.sidebar:
    st.title("Main Menu")
    page_mode = st.radio("", ["1. Trap Monitor", "2. Inertia Grid", "3. Quick Links"])
    st.write("---")
    st.write("### Trap Setting")
    sigma_val = st.slider("Deviation Level", 1.0, 3.0, 1.5, 0.1)

# 3. メインパネル

# --- 1枚目：表紙（リンクなし・監視集中） ---
if page_mode == "1. Trap Monitor":
    st.title("Statistical Trap Monitor")
    for ticker in symbols:
        data = get_data(ticker)
        target_kairi = data['Kairi'].mean() - (sigma_val * data['Kairi'].std())
        
        fig, ax = plt.subplots(figsize=(10, 3))
        fig.patch.set_facecolor('white')
        ax.set_facecolor('white')
        ax.plot(data.index, data['Kairi'], color='#3b82f6', linewidth=2)
        ax.axhline(y=target_kairi, color='#ef4444', linestyle='--', linewidth=1.5)
        ax.set_title(f"{ticker} : {symbol_map[ticker]}", color='black', loc='left', fontsize=10, fontweight='bold')
        ax.grid(True, linestyle='--', alpha=0.3, color='#ccc')
        st.pyplot(fig)
        
        st.write(f"Dev: **{data['Kairi'].iloc[-1]:.2f}%** / TARGET: :red[**{target_kairi:.2f}%**]")
        st.write("---")

# --- 2枚目：慣性グリッド（リンクなし・執行判断） ---
elif page_mode == "2. Inertia Grid":
    st.title("Inertia & Deviation Grid")
    for ticker in symbols:
        data = get_data(ticker)
        target_kairi = data['Kairi'].mean() - (sigma_val * data['Kairi'].std())
        target_price = data['MA25'].iloc[-1] * (1 + target_kairi / 100)
        
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 8), sharex=True, gridspec_kw={'height_ratios': [2, 1]})
        fig.patch.set_facecolor('white')
        ax1.set_facecolor('white')
        ax1.plot(data.index, data['Close'], color='black', linewidth=1.5)
        ax1.plot(data.index, data['MA25'], color='#ff9800', linestyle='--', linewidth=1)
        ax1.set_title(f"{ticker} : {symbol_map[ticker]}", color='black', loc='left', fontsize=12, fontweight='bold')
        ax1.grid(True, linestyle='--', alpha=0.3, color='#ccc')
        
        ax2.set_facecolor('white')
        ax2.plot(data.index, data['Kairi'], color='#7e57c2', linewidth=1.5)
        ax2.axhline(y=target_kairi, color='#ef4444', linestyle='--', linewidth=1.5)
        ax2.grid(True, linestyle='--', alpha=0.3, color='#ccc')
        st.pyplot(fig)
        
        st.markdown(f"Price: **{data['Close'].iloc[-1]:,.1f}** / TARGET: :red[**{target_price:,.1f} JPY**]")
        st.write("---")

# --- 3枚目：ここで初めてリンクを表示 ---
elif page_mode == "3. Quick Links":
    st.title("External Analysis Links")
    st.write("銘柄名を選択して詳細情報を確認します。")
    st.write("---")
    
    for ticker in symbols:
        name = symbol_map[ticker]
        # 日本のヤフーファイナンスのURLを動的に生成
        y_url = f"https://finance.yahoo.co.jp/quote/{ticker}"
        
        st.subheader(f"{name} ({ticker})")
        # ここにだけリンクを設置
        st.link_button(f"Go to Yahoo! Finance", y_url, use_container_width=True)
        st.write("---")

st.caption(f"Last Synced: {datetime.datetime.now().strftime('%H:%M:%S')}")
