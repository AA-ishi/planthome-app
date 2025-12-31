import streamlit as st
from PIL import Image
import base64
import pandas as pd
import requests

# ===============================
# Sakura AI（agent API）設定
# ===============================
API_TOKEN = st.secrets["SAKURA_API_KEY"]
API_URL = "https://api.ai.sakura.ad.jp/v1/chat/completions"

HEADERS = {
    "Authorization": f"Bearer {st.secrets['SAKURA_API_KEY']}",
    "Content-Type": "application/json",
}
# ===============================
# 背景画像設定
# ===============================
def set_background(image_path):
    with open(image_path, "rb") as img_file:
        encoded = base64.b64encode(img_file.read()).decode()
    st.markdown(
        f"""
        <style>
        .stApp {{
            background-image: url("data:image/png;base64,{encoded}");
            background-size: cover;
            background-position: center;
            background-repeat: no-repeat;
        }}
        </style>
        """,
        unsafe_allow_html=True
    )

set_background("appback20250822.png")

# ===============================
# 共通CSS（タイトル＋スマホ＋ダークモード全部ここ）
# ===============================
st.markdown("""
<style>
html, body, [class*="css"] {
    color: #000 !important;
    background-color: rgba(255, 255, 255, 0.0) !important;
}
input, select, textarea {
    color: #000 !important;
    background-color: #ffffff !important;
}
div.stButton > button:first-child {
    color: #333 !important;
}

#/* タイトル */
.title-text {
    font-size: 48px;
    font-weight: bold;
    color: white;
    text-align: center;
    text-shadow:
        -2px -2px 0 #000,
         2px -2px 0 #000,
        -2px  2px 0 #000,
         2px  2px 0 #000;
    margin-top: 30px;
    margin-bottom: 10px;
}

/* サブタイトル */
.subtitle-text {
    font-size: 24px;
    color: white;
    text-align: center;
    text-shadow: 1px 1px 2px #000;
    margin-bottom: 10px;
}

/* スマホ最適化 */
@media screen and (max-width: 480px) {
    .title-text {
        font-size: 32px;
        margin-top: 6px;
        margin-bottom: 6px;
    }
    .subtitle-text {
        font-size: 18px;
    }
    input, select, textarea {
        font-size: 16px;
    }
}


</style>
""", unsafe_allow_html=True)
# ===============================
# タイトル
# ===============================
st.markdown("""
<div class='title-text'>室内観葉植物のお手入れ方法</div>
<div class='subtitle-text'>How to care for indoor plants</div>
""", unsafe_allow_html=True)

# ===============================
# 入力UI
# ===============================
plant_name = st.text_input("🌱 植物の名前を入力してください:")
location = st.selectbox(
    "🏠 置いてある場所を選択してください:",
    [
        "日がよく当たる窓際",
        "あまり日が当たらない窓際",
        "明るいけれど窓際ではない場所",
        "日が当たらない場所"
     ],
    key="location_select"
)

# ===============================
# ボタン（サイズ・装飾復活）
# ===============================
st.markdown("""
<style>
.stButton > button {
    display: block;
    margin: 0 auto;
    background-color: #ffe4e1 !important;
    color: #333 !important;
    border: none;
    padding: 0.6em 1.2em;
    font-size: 16px;
    border-radius: 6px;
}
</style>
""", unsafe_allow_html=True)

col1, col2, col3 = st.columns([1, 1, 1])
with col2:
    clicked = st.button("クリックしてね 💧🌿", key="main_button")

# ===============================
# 水やり頻度計算
# ===============================
def calculate_watering_frequency(base_days, location):
    if location == "日がよく当たる窓際":
        return base_days
    elif location == "あまり日が当たらない窓際":
        return base_days + 2
    elif location == "明るいけれど窓際ではない場所":
        return base_days + 1
    elif location == "日が当たらない場所":
        return base_days + 5
    return base_days

# ===============================
# 水やり表示
# ===============================
if plant_name and location:
    try:
        df = pd.read_csv("plant_database.csv")
        match = df[df["名前"] == plant_name]

        if not match.empty:
            base_days = int(match.iloc[0]["推奨頻度_日"])
            adjusted_days = calculate_watering_frequency(base_days, location)
            st.markdown("💧 水やり頻度")
            st.write(
                f"{adjusted_days} 日ごとに水やりをしてみましょう。"
                "お水をあげるときは鉢底から水が流れ出るぐらいタップリあげてください。"
                "植物の様子をみて頻度を変えることも必要です。"
            )
        else:
            st.warning("水やりの頻度は育て方を参考にしてください。")
    except Exception as e:
        st.error(f"CSVの読み込みに失敗しました: {e}")

# ===============================
# AI 管理アドバイス（agent API）
# ===============================
st.markdown("🌿 管理方法")

if clicked and plant_name:
    prompt = f"""
    {plant_name} の室内管理方法を園芸初心者でもわかるように書く。
    260字程度でまとめる。
    {plant_name}が植物ではない場合は{plant_name}の紹介をする。
    {plant_name}が植物を含むときは育てる環境（屋内/屋外）、温度、湿度、注意点を含める。
    最後は育てるのが楽しくなるようなメッセージをつけて。
    """

    payload = {
        "model": "llm-jp-3.1-8x13b-instruct4",
        "messages": [
            {
                "role": "system",
                "content": (
                    "あなたは親しみやすく、ユーモアのある植物を育てる専門家です。"                                   
                )
            },
            {
                "role": "user",
                "content": prompt
            }
        ],
        "temperature": 0.7,
        "max_tokens": 300,
    }

    with st.spinner("AIが考えています🌱"):
        r = requests.post(API_URL, headers=HEADERS, json=payload)

    if r.status_code == 200:
        result = r.json()
        st.write(result["choices"][0]["message"]["content"])
    else:
        st.error(f"APIエラー {r.status_code}: {r.text}")

else:
    st.info("植物の名前と置き場所を入れてボタンをクリックしてください 🌱")
