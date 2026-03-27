import streamlit as st
import json
import sqlite3
import random
from datetime import datetime

# ---------------------------------------------------------
# ページ設定（スマホ最適化）
# ---------------------------------------------------------
st.set_page_config(page_title="瞬間英作文アプリ", layout="wide")

# ---------------------------------------------------------
# 今ある JSON ファイルだけの FILE_MAP（完全版）
# ---------------------------------------------------------
FILE_MAP = {
    "第2文型（SVC）": "data/bunkei2.json",
    "第3文型（SVO）": "data/bunkei3.json",
    "第4文型（SVOO）": "data/bunkei4.json",
    "第5文型（SVOC）": "data/bunkei5.json",

    "現在形": "data/present_simple.json",
    "過去形": "data/past_simple.json",
    "未来形": "data/future_simple.json",

    "現在完了形": "data/present_perfect.json",
    "受動態": "data/passive.json",
    "動名詞": "data/gerund.json",
    "不定詞": "data/infinitive.json",

    "現在進行形": "data/present_continuous.json",
    "現在完了進行形": "data/present_perfect_continuous.json",

    "関係代名詞": "data/relative_pronoun.json",
    "仮定法": "data/conditional.json",

    "動詞": "data/verb.json",
    "take": "data/take.json",
    "make": "data/make.json",
    "keep": "data/keep.json",
    "shall": "data/shall.json",
    "can": "data/can.json",

    "get": "data/get.json",
    "have": "data/have.json",
    "give": "data/give.json"
}

# ---------------------------------------------------------
# JSON 読み込み
# ---------------------------------------------------------
def load_questions(category):
    path = FILE_MAP[category]
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

# ---------------------------------------------------------
# 履歴DB
# ---------------------------------------------------------
def init_db():
    conn = sqlite3.connect("history.db")
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            category TEXT,
            japanese TEXT,
            english TEXT,
            result TEXT,
            timestamp TEXT
        )
    """)
    conn.commit()
    conn.close()

def save_history(category, japanese, english, result):
    conn = sqlite3.connect("history.db")
    c = conn.cursor()
    c.execute("""
        INSERT INTO history (category, japanese, english, result, timestamp)
        VALUES (?, ?, ?, ?, ?)
    """, (category, japanese, english, result, datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
    conn.commit()
    conn.close()

def load_history():
    conn = sqlite3.connect("history.db")
    c = conn.cursor()
    c.execute("SELECT * FROM history ORDER BY id DESC LIMIT 5000")
    rows = c.fetchall()
    conn.close()
    return rows

init_db()

# ---------------------------------------------------------
# UI（スマホ1画面完結）
# ---------------------------------------------------------
st.title("📘 瞬間英作文トレーニング")

# ★ サイドバー完全廃止 → メイン画面にメニュー配置
mode = st.selectbox(
    "モードを選択してください",
    ["トレーニング", "履歴", "管理"],
    index=0
)

# ---------------------------------------------------------
# トレーニングモード
# ---------------------------------------------------------
if mode == "トレーニング":
    st.header("📝 トレーニング")

    category = st.selectbox("カテゴリーを選択", list(FILE_MAP.keys()))
    questions = load_questions(category)
    question = random.choice(questions)

    st.subheader("日本語：")
    st.write(question["japanese"])

    if st.button("答えを見る"):
        st.success(question["english"])

    col1, col2 = st.columns(2)
    with col1:
        if st.button("できた！"):
            save_history(category, question["japanese"], question["english"], "correct")
            st.success("記録しました！")

    with col2:
        if st.button("できなかった…"):
            save_history(category, question["japanese"], question["english"], "wrong")
            st.error("記録しました！")

# ---------------------------------------------------------
# 履歴モード
# ---------------------------------------------------------
elif mode == "履歴":
    st.header("📊 履歴")

    rows = load_history()
    st.write(f"最新 {len(rows)} 件を表示")

    for row in rows:
        st.write(f"【{row[5]}】 {row[1]} / {row[2]} → {row[4]}")

# ---------------------------------------------------------
# 管理モード（今は空）
# ---------------------------------------------------------
elif mode == "管理":
    st.header("⚙ 管理モード")
    st.write("ここに問題追加機能などを配置できます。")














