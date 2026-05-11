import streamlit as st
import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt
import datetime

# 1. 共通設定
symbol_map = {'6255.T': 'NPC', '464A.T': 'QPS Institute', '3778.T': 'Sakura Internet'}
symbols = list(symbol_map.keys())

@st.cache_data(ttl=300)
def get_data_and_stats(ticker):
    # 150日間の母集団確保のため180日取得（MA25計算用のバッファ含む）
    data = yf.download(ticker, period="180d", interval="1d", auto_adjust=True, progress=False)
    if isinstance(data.columns, pd.MultiIndex):
        data.columns = data.columns.get_level_values(0)
    df = data.dropna(subset=['Close']).copy()
    df['MA25'] = df['Close'].rolling(window=25).mean()
    df['Kairi'] = ((df['Close'] - df['MA25']) / df['MA25']) * 100
    
    # 偏差値算出（最新150日分を対象）
    df_stat = df.dropna(subset=['Kairi']).tail(150).copy()
    m, s = df_stat['Kairi'].mean(), df_stat['Kairi'].std()
    df_stat['T_Score'] = 50 + 10 * (df_stat['Kairi'] - m) / s
    return df_stat, m, s

# --- メインパネル構成 ---
with st.sidebar:
    st.title("Main Menu")
    # 1枚目を削除し、2面構成に変更
    page = st.radio("", ["1. Analysis Grid", "2. News Panel"])
    st.write("---")
    st.caption(f"Last Synced: {datetime.datetime.now().strftime('%H:%M:%S')}")

# --- 1. 統合グリッド（執行判断） ---
if page == "1. Analysis Grid":
    st.title("Inertia & Statistics Grid")
    for ticker in symbols:
        df, m, s = get_data_and_stats(ticker)
        
        # ターゲット価格逆算 (偏差値40と35)
        def calc_p(t):
            k = ((t - 50) / 10) * s + m
            return df['MA25'].iloc[-1] * (1 + k / 100)
        
        p40, p35 = calc_p(40), calc_p(35)
        cur_p = df['Close'].iloc[-1]
        cur_t = df['T_Score'].iloc[-1]

        # グラフ描画
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 6), sharex=True, gridspec_kw={'height_ratios': [2, 1]})
        ax1.plot(df.index, df['Close'], color='black', linewidth=1.5)
        ax1.plot(df.index, df['MA25'], color='orange', linestyle='--', linewidth=1)
        ax1.set_title(f"{symbol_map[ticker]} ({ticker})", loc='left', fontweight='bold')
        
        ax2.plot(df.index, df['T_Score'], color='#7e57c2', linewidth=2)
        ax2.axhline(40, color='orange', linestyle='--', label='T40')
        ax2.axhline(35, color='red', linestyle='--', label='T35')
        ax2.set_ylim(25, 75)
        ax2.legend(loc='upper left')
        st.pyplot(fig)
        
        # 数値パネル（執行価格の明示）
        st.markdown(f"**現在価格: {cur_p:,.1f}** (現在偏差値: {cur_t:.1f})")
        st.markdown(f":orange[**T40 (Warning): {p40:,.1f}**] / :red[**T35 (Trap): {p35:,.1f}**]")
        st.write("---")

# --- 2. ニュースパネル（Yahoo!ファイナンスへのダイレクトリンク） ---
elif page == "2. News Panel":
    st.title("External Links")
    st.info("銘柄の詳細情報・ニュースは、Yahoo!ファイナンスで確認してください。")
    
    for ticker in symbols:
        # ティッカー（例: 6255.T）から数字部分のみを抽出
        code = ticker.split('.')[0]
        name = symbol_map[ticker]
        
        st.subheader(f"{name} ({ticker})")
        
        # Yahoo!ファイナンス 日本版の銘柄詳細URL
        yahoo_url = f"https://finance.yahoo.co.jp/quote/{code}.T"
        
        # シンプルにリンクボタンのみ配置
        st.link_button(f"Yahoo!ファイナンスで {name} を開く", yahoo_url, use_container_width=True)
        st.write("---")
