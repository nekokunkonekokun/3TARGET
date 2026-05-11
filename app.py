import streamlit as st
import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt
import datetime

# 1. 共通設定
symbol_map = {
    '6255.T': 'NPC',
    '464A.T': 'QPS Institute',
    '3778.T': 'Sakura Internet'
}
symbols = list(symbol_map.keys())

# --- 共通データ取得関数 ---
@st.cache_data(ttl=300)
def get_data(ticker):
    # 【修正】30分足(interval="30m")で取得。
    # 150本分表示したいので、MA25用に余裕を見て直近7日間(7d)取得
    data = yf.download(ticker, period="7d", interval="30m", auto_adjust=True)
    if data.empty: return pd.DataFrame()
    
    if isinstance(data.columns, pd.MultiIndex):
        data.columns = data.columns.get_level_values(0)
    
    data = data.dropna(subset=['Close'])
    data['MA25'] = data['Close'].rolling(window=25).mean()
    data['Kairi'] = ((data['Close'] - data['MA25']) / data['MA25']) * 100
    
    # 計算でNaNになった最初の24本を捨て、直近150本を抽出
    data = data.dropna(subset=['Kairi']).tail(150)
    return data

def plot_compact(data, ticker, sigma_val, mode="monitor"):
    data_reset = data.reset_index()
    # 【修正】X軸ラベルを「月-日 時:分」に変更
    data_reset['Time_str'] = data_reset['Datetime'].dt.strftime('%m-%d %H:%M')
    x = data_reset.index
    
    target_kairi = data['Kairi'].mean() - (sigma_val * data['Kairi'].std())
    
    if mode == "monitor":
        fig, ax = plt.subplots(figsize=(10, 3))
        ax.plot(x, data_reset['Kairi'], color='#3b82f6', linewidth=2)
        ax.axhline(y=target_kairi, color='#ef4444', linestyle='--')
        ax.set_title(f"{ticker} (30m)", loc='left', fontweight='bold')
    else:
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 8), sharex=True, gridspec_kw={'height_ratios': [2, 1]})
        ax1.plot(x, data_reset['Close'], color='black', linewidth=1.5)
        ax1.plot(x, data_reset['MA25'], color='#ff9800', linestyle='--')
        ax2.plot(x, data_reset['Kairi'], color='#7e57c2', linewidth=1.5)
        ax2.axhline(y=target_kairi, color='#ef4444', linestyle='--')
        ax = ax2
        
    # ラベルが密集するので30本おきに表示
    xticks = x[::30]
    ax.set_xticks(xticks)
    ax.set_xticklabels(data_reset['Time_str'].iloc[xticks], fontsize=8, rotation=0)
    
    fig.patch.set_facecolor('white')
    for a in fig.axes:
        a.set_facecolor('white')
        a.grid(True, linestyle='--', alpha=0.3)
    return fig

# 2. サイドバー
with st.sidebar:
    st.title("Main Menu")
    page_mode = st.radio("", ["1. Trap Monitor", "2. Inertia Grid", "3. Quick Links"])
    sigma_val = st.slider("Deviation Level", 1.0, 3.0, 1.5, 0.1)

# 3. メインパネル
if page_mode == "1. Trap Monitor" or page_mode == "2. Inertia Grid":
    st.title(f"{page_mode}")
    for ticker in symbols:
        data = get_data(ticker)
        if data.empty: continue
        
        mode_str = "monitor" if page_mode == "1. Trap Monitor" else "grid"
        st.pyplot(plot_compact(data, ticker, sigma_val, mode_str))
        
        target_kairi = data['Kairi'].mean() - (sigma_val * data['Kairi'].std())
        if page_mode == "1. Trap Monitor":
            st.write(f"Dev: **{data['Kairi'].values[-1]:.2f}%** / TARGET: :red[**{target_kairi:.2f}%**]")
        else:
            target_price = data['MA25'].values[-1] * (1 + target_kairi / 100)
            st.markdown(f"Price: **{data['Close'].values[-1]:,.1f}** / TARGET: :red[**{target_price:,.1f} JPY**]")
        st.write("---")

elif page_mode == "3. Quick Links":
    st.title("External Analysis Links")
    for ticker in symbols:
        st.subheader(f"{symbol_map[ticker]} ({ticker})")
        st.link_button("Go to Yahoo! Finance", f"https://finance.yahoo.co.jp/quote/{ticker}", use_container_width=True)

st.caption(f"Last Synced: {datetime.datetime.now().strftime('%H:%M:%S')}")
