import streamlit as st
import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt

# 1. 監視対象の設定（日本語銘柄名の辞書）
symbol_map = {
    '6255.T': 'NPC',
    '464A.T': 'QPS',
    '3778.T': 'さくらインターネット'
}
symbols = list(symbol_map.keys())

# 2. サイドバー（画像5の引きずり出しメニューを再現）
with st.sidebar:
    st.title("Main Menu")
    menu = st.radio("", ["Dashboard", "News", "The Prison"])
    st.write("---")
    st.write("### 罠の設定 (Target 35)")
    # 偏差値35（-1.5σ）をデフォルトに。スライダーで微調整可能
    sigma_val = st.slider("Deviation Level", 1.0, 3.0, 1.5, 0.1)
    st.write("※1.5σ(偏差値35)付近が『美味しそうな形』の目安です。")

# 3. メインパネル（3枚のチャートを縦に並べる）
st.title("Statistical Trap Monitor")

for ticker in symbols:
    name = symbol_map[ticker]
    
    # データ取得（エラー対策のためauto_adjust=Trueを推奨）
    data = yf.download(ticker, period="150d", auto_adjust=True)
    
    # 【重要】ValueError対策：多重階層の列名をフラットにする
    if isinstance(data.columns, pd.MultiIndex):
        data.columns = data.columns.get_level_values(0)
    
    # データの欠損を排除
    data = data.dropna(subset=['Close'])

    # 統計計算（25日移動平均と乖離率）
    data['MA25'] = data['Close'].rolling(window=25).mean()
    data['Kairi'] = ((data['Close'] - data['MA25']) / data['MA25']) * 100
    
    # ターゲット値（過去の平均乖離率 - N倍の標準偏差）
    mean_kairi = data['Kairi'].mean()
    std_kairi = data['Kairi'].std()
    target_line = mean_kairi - (sigma_val * std_kairi)

    # 現在の状況を取得
    current_kairi = data['Kairi'].iloc[-1]
    
    # チャート描画（黒背景、青線、赤点線）
    fig, ax = plt.subplots(figsize=(10, 4), facecolor='black')
    ax.set_facecolor('black')
    
    # 乖離率の推移（青線）
    ax.plot(data.index, data['Kairi'], color='#3b82f6', linewidth=2, label='Current Dev')
    # 罠のライン（赤点線）
    ax.axhline(y=target_line, color='#ef4444', linestyle='--', linewidth=1.5, label='Target 35')
    
    # 軸・タイトルの装飾（ノイズ排除）
    ax.tick_params(axis='x', colors='#666', labelsize=8)
    ax.tick_params(axis='y', colors='#666', labelsize=8)
    ax.set_title(f"{ticker} : {name}", color='white', loc='left', fontsize=12, fontweight='bold')
    
    # チャート表示
    st.pyplot(fig)
    
    # 数値情報
    col1, col2 = st.columns(2)
    with col1:
        st.write(f"現在の乖離率: **{current_kairi:.2f}%**")
    with col2:
        st.write(f"罠の着弾点 (Target): :red[**{target_line:.2f}%**]")
    
    st.write("---") # 銘柄ごとの区切り

st.caption("2026.05.07 - Statistical Predator System. 獲物が檻にかかるまで指を差して待つのみ。")
