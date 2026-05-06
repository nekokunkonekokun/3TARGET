import streamlit as st
import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt

# 1. 記号と日本語名のマッピング（辞書直書きで安定化）
symbol_map = {
    '6255.T': 'NPC',
    '464A.T': 'QPS研究所',
    '3778.T': 'さくらインターネット'
}
symbols = list(symbol_map.keys())

# 2. サイドバー（引きずり出しメニュー）
with st.sidebar:
    st.title("Main Menu")
    st.radio("", ["Dashboard", "News", "The Prison"])
    st.write("---")
    st.write("### 罠の設定 (Target 35)")
    sigma_val = st.slider("Deviation Level", 1.0, 3.0, 1.5, 0.1)

# 3. メインパネル（3枚のチャートを縦に並べる）
st.title("Statistical Trap Monitor")

for ticker in symbols:
    name = symbol_map[ticker]
    data = yf.download(ticker, period="120d")
    
    # 統計計算
    data['MA25'] = data['Close'].rolling(window=25).mean()
    data['Kairi'] = ((data['Close'] - data['MA25']) / data['MA25']) * 100
    target_line = data['Kairi'].mean() - (sigma_val * data['Kairi'].std())

    # チャート描画
    fig, ax = plt.subplots(figsize=(10, 4), facecolor='black')
    ax.set_facecolor('black')
    ax.plot(data.index, data['Kairi'], color='#3b82f6', linewidth=2)
    ax.axhline(y=target_line, color='#ef4444', linestyle='--', linewidth=1.5)
    
    # タイトルに日本語名を付与（フォント設定は環境に依存するため標準で対応）
    ax.set_title(f"{ticker} : {name}", color='white', loc='left', fontsize=12)
    
    st.pyplot(fig)
    
    current_kairi = data['Kairi'].iloc[-1]
    st.write(f"Current: {current_kairi:.2f}% | **Target: {target_line:.2f}%**")
    st.write("---")

