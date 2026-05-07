import streamlit as st
import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt

# 1. 共通設定（英語表記で固定）
symbol_map = {
    '6255.T': 'NPC',
    '464A.T': 'QPS Institute',
    '3778.T': 'Sakura Internet'
}
symbols = list(symbol_map.keys())

# --- 共通データ取得関数 ---
@st.cache_data(ttl=300) # 5分間キャッシュ
def get_data(ticker):
    data = yf.download(ticker, period="150d", auto_adjust=True)
    if isinstance(data.columns, pd.MultiIndex):
        data.columns = data.columns.get_level_values(0)
    data = data.dropna(subset=['Close'])
    data['MA25'] = data['Close'].rolling(window=25).mean()
    data['Kairi'] = ((data['Close'] - data['MA25']) / data['MA25']) * 100
    return data

# 2. サイドバー（引き出しメニュー）
with st.sidebar:
    st.title("Main Menu")
    # ここでの選択が `page_mode` に格納される
    page_mode = st.radio("", ["1. Trap Monitor (Dev)", "2. Inertia Grid (Price)", "3. News"])
    st.write("---")
    st.write("### Trap Setting")
    sigma_val = st.slider("Deviation Level", 1.0, 3.0, 1.5, 0.1)

# 3. メインパネル（選択されたページ・モードによって表示を切り替える）

# --- モード1：Trap Monitor (現在の乖離率1枚パネル) ---
if page_mode == "1. Trap Monitor (Dev)":
    st.title("Statistical Trap Monitor (Deviation)")
    for ticker in symbols:
        name = symbol_map[ticker]
        data = get_data(ticker)
        
        # ターゲット乖離率
        target_kairi = data['Kairi'].mean() - (sigma_val * data['Kairi'].std())
        
        # チャート描画（白背景、乖離率のみ）
        fig, ax = plt.subplots(figsize=(10, 3))
        fig.patch.set_facecolor('white')
        ax.set_facecolor('white')
        ax.plot(data.index, data['Kairi'], color='#3b82f6', linewidth=2)
        ax.axhline(y=target_kairi, color='#ef4444', linestyle='--', linewidth=1.5)
        ax.set_title(f"{ticker} : {name}", color='black', loc='left', fontsize=10, fontweight='bold')
        ax.grid(True, linestyle='--', alpha=0.3, color='#ccc')
        st.pyplot(fig)
        
        # 数値情報
        cur_kairi = data['Kairi'].iloc[-1]
        st.write(f"Current Dev: **{cur_kairi:.2f}%** / TARGET: :red[**{target_kairi:.2f}%**]")
        st.write("---")

# --- モード2：Inertia Grid (画像1の2段チャート、価格と25日線) ---
elif page_mode == "2. Inertia Grid (Price)":
    st.title("Inertia & Deviation Grid (Price vs Trap)")
    for ticker in symbols:
        name = symbol_map[ticker]
        data = get_data(ticker)
        
        # 計算
        target_kairi = data['Kairi'].mean() - (sigma_val * data['Kairi'].std())
        current_ma25 = data['MA25'].iloc[-1]
        target_price = current_ma25 * (1 + target_kairi / 100)
        current_price = data['Close'].iloc[-1]
        
        # --- 画像1のような、上下2段チャートを作成 ---
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 8), sharex=True, 
                                       gridspec_kw={'height_ratios': [2, 1]})
        fig.patch.set_facecolor('white')
        
        # 上段：株式相場（Price）と25日線（Inertia）
        ax1.set_facecolor('white')
        ax1.plot(data.index, data['Close'], color='black', linewidth=1.5, label='Price')
        ax1.plot(data.index, data['MA25'], color='#ff9800', linestyle='--', linewidth=1, label='MA25 (Inertia)') # オレンジの点線
        ax1.set_title(f"{ticker} : {name}", color='black', loc='left', fontsize=12, fontweight='bold')
        ax1.grid(True, linestyle='--', alpha=0.3, color='#ccc')
        ax1.legend(loc='best', fontsize=8)
        
        # 下段：乖離率（Deviation）と罠（Target 35）
        ax2.set_facecolor('white')
        ax2.plot(data.index, data['Kairi'], color='#7e57c2', linewidth=1.5) # 紫線
        ax2.axhline(y=target_kairi, color='#ef4444', linestyle='--', linewidth=1.5) # 赤点線
        ax2.grid(True, linestyle='--', alpha=0.3, color='#ccc')
        
        st.pyplot(fig)
        
        # 価格情報の数値
        st.markdown(f"Current Price: **{current_price:,.1f} JPY** / TARGET PRICE: :red[**{target_price:,.1f} JPY**]")
        st.write("---")

# --- モード3：News (画像3の外部要因監視) ---
elif page_mode == "3. News":
    st.title("Target Symbol News (JP)")
    
    # 検索精度を上げるためのキーワード設定
    jp_names = {
        '6255.T': 'NPC 太陽電池',
        '464A.T': 'QPS研究所 宇宙',
        '3778.T': 'さくらインターネット AI'
    }

    if st.button("Fetch Latest 10 News"):
        with st.spinner("国内の最新材料をスキャン中..."):
            import urllib.parse
            for ticker, query in jp_names.items():
                st.subheader(f"Latest Trends: {query}")
                
                # GoogleニュースRSS（日本語・日本地域設定）
                encoded_query = urllib.parse.quote(query)
                rss_url = f"https://news.google.com/rss/search?q={encoded_query}&hl=ja&gl=JP&ceid=JP:ja"
                
                try:
                    # pd.read_xmlでRSSをパースし、最新10件を取得
                    df_news = pd.read_xml(rss_url, xpath=".//item")
                    # head(10)で最新10件に固定
                    for _, item in df_news.head(10).iterrows():
                        # タイトルとソース、日付をコンパクトに表示
                        st.markdown(f"**{item['title']}**")
                        st.caption(f"{item['source']} | {item['pubDate']}")
                except Exception:
                    st.write("現在、この銘柄に関する直近のニュースは見つかりませんでした。")
                
                st.write("---") # 銘柄ごとの仕切り
    else:
        st.info("ボタンを押すと、各銘柄の最新ニュース10件を時系列で取得します。")
