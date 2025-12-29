import streamlit as st
from PIL import Image
import base64
import pandas as pd
import requests

# シークレットキーの取得
api_key = st.secrets["SAKURA_API_KEY"]
endpoint = "https://api.ai.sakura.ad.jp/v1/chat/completions"


# 背景画像の設定
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

# 背景画像を設定
set_background("appback20250822.png")

# 共通CSSスタイル
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
    .title-text {
        font-size: 44px;
        font-weight: bold;
        color: white;
        text-align: center;
        text-shadow:
            -2px -2px 0 #000,
             2px -2px 0 #000,
            -2px  2px 0 #000,
             2px  2px 0 #000;
        margin-top: 10px;
        margin-bottom: 8px;
    }
    .subtitle-text {
        font-size: 24px;
        color: white;
        text-align: center;
        text-shadow: 1px 1px 2px #000;
        margin-bottom: 10px;
    }
    </style>
""", unsafe_allow_html=True)

# タイトル表示
st.markdown("""
    <div class='title-text'>室内観葉植物のお手入れ方法</div>
    <div class='subtitle-text'>How to care for indoor plants</div>
""", unsafe_allow_html=True)

# 入力欄
plant_name = st.text_input("🌱 植物の名前を入力してください:", key="plant_name_input")
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

# クリックボタンの設定
st.markdown("""
    <style>
    .stButton > button {
        display: block;
        margin: 0 auto;
        background-color: #ffe4e1 !important;  /* 薄い桜色 */
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
    action = st.button("クリックしてね 💧🌿", key="main_button")

# 水やり頻度の補正ロジック
def calculate_watering_frequency(base_days, location):
    if location == "日がよく当たる窓際":
        return base_days
    elif location == "あまり日が当たらない窓際":
        return base_days + 2
    elif location == "明るいけれど窓際ではない場所":
        return base_days + 1
    elif location == "日が当たらない場所":
        return base_days + 5
    else:
        return base_days

# 水やり頻度の表示
if plant_name and location:
    try:
        df = pd.read_csv("plant_database.csv")
        match = df[df["名前"] == plant_name]

        if not match.empty:
            base_days = int(match.iloc[0]["推奨頻度_日"])
            adjusted_days = calculate_watering_frequency(base_days, location)
            st.markdown("💧 水やり頻度")
            watering_text = (
                f"{adjusted_days} 日ごとに水やりをしてみましょう。"
                "お水をあげるときは鉢底から水が流れ出るぐらいタップリあげてください。"
                "植物の様子をみて頻度を変えることも必要です。"
            )
            st.write(watering_text)
        else:
            st.warning("水やりの頻度は育て方を参考にしてください。")
    except Exception as e:
        st.error(f"CSVの読み込みに失敗しました。ファイルや列名をご確認ください。\n\n詳細: {e}")

# ⚠ warningスタイルの簡素化（これは if-else の外でもOK）
st.markdown("""
<style>
div[class*="stAlert"] {
    background-color: transparent !important;
    border: none !important;
    box-shadow: none !important;
}
</style>
""", unsafe_allow_html=True)

# 管理方法の表
st.markdown("🌿 管理方法")

if plant_name:
    prompt = f"""
    {plant_name} の室内管理方法を、園芸初心者にもわかるように、260字程度で完結させてください。
    {plant_name}が植物でない場合は{plant_name}の紹介をしてください。
    置き場所（屋内屋外どちらがいいのか）、室内で育てた場合の温度、湿度、その他の注意点などを教えてください。
    """

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }

    body = {
        "model": "llm-jp-3.1.8x13b-instruct4",
        "messages": [
            {"role": "system", "content": "あなたはユーモアのある植物ケアの専門家です。"},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.7,
        "max_tokens": 400
    }

    try:
        response = requests.post(endpoint, headers=headers, json=body)
        result = response.json()
        st.write(result)

        if "choices" in result and len(result["choices"]) > 0:
            advice = result["choices"][0]["message"]["content"]
            st.write(advice)
        else:
            st.error("AIからの回答が取得できませんでした。")
    except Exception as e:
        st.error(f"リクエスト中にエラーが発生しました: {e}")


else:
    st.warning("植物の名前と置き場所をいれてボタンをクリックすると、管理方法のアドバイスが表示されます🌱")
    















