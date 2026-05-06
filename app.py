import streamlit as st
import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt

# 1. 監視対象の設定
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

# 3. メインパネル
st.title("Statistical Trap Monitor")

for ticker in symbols:
    name = symbol_map[ticker]
    data = yf.download(ticker, period="150d", auto_adjust=True)
    
    if isinstance(data.columns, pd.MultiIndex):
        data.columns = data.columns.get_level_values(0)
    
    data = data.dropna(subset=['Close'])

    # 統計計算
    data['MA25'] = data['Close'].rolling(window=25).mean()
    data['Kairi'] = ((data['Close'] - data['MA25']) / data['MA25']) * 100
    
    # ターゲット乖離率の計算
    target_kairi = data['Kairi'].mean() - (sigma_val * data['Kairi'].std())
    
    # 【重要】ターゲット価格の算出
    # 価格 = MA25 * (1 + target_kairi / 100)
    current_ma25 = data['MA25'].iloc[-1]
    target_price = current_ma25 * (1 + target_kairi / 100)
    current_price = data['Close'].iloc[-1]

    # チャート描画（白背景に変更）
    fig, ax = plt.subplots(figsize=(10, 4), facecolor='white')
    ax.set_facecolor('white')
    
    ax.plot(data.index, data['Kairi'], color='#3b82f6', linewidth=2, label='Current Dev')
    ax.axhline(y=target_kairi, color='#ef4444', linestyle='--', linewidth=1.5, label='Target 35')
    
    # グリッドを追加して視認性向上
    ax.grid(True, which='both', linestyle='--', alpha=0.5)
    ax.tick_params(axis='both', colors='#333', labelsize=8)
    ax.set_title(f"{ticker} : {name}", color='black', loc='left', fontsize=12, fontweight='bold')
    
    st.pyplot(fig)
    
    # 数値情報：Target価格を強調表示
    col1, col2, col3 = st.columns(3)
    with col1:
        st.write(f"現在値: **{current_price:,.1f}円**")
    with col2:
        st.write(f"現在乖離: **{data['Kairi'].iloc[-1]:.2f}%**")
    with col3:
        st.markdown(f"着弾価格: :red[**{target_price:,.1f}円**]")
    
    st.write("---")

st.caption("2026.05.07 - 価格という獲物の急所を射抜く。")
