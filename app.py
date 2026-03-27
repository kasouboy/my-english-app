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
# カテゴリとファイルマップ（文法カテゴリすべて統合）
# ---------------------------------------------------------
FILE_MAP = {
    "基本文型": "data/basic.json",
    "動詞": "data/verb.json",
    "助動詞": "data/modal.json",
    "時制": "data/tense.json",
    "文法": "data/grammar.json",

    # 追加してきた動詞シリーズ
    "take": "data/take.json",
    "make": "data/make.json",
    "keep": "data/keep.json",
    "shall": "data/shall.json",
    "get": "data/get.json",
    "have": "data/have.json",
    "give": "data/give.json",
    "put": "data/put.json",
    "bring": "data/bring.json",
    "go": "data/go.json",
    "come": "data/come.json",
    "see": "data/see.json",
    "look": "data/look.json",
    "watch": "data/watch.json",
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

# ★ サイドバー廃止 → メイン画面にメニュー配置
mode = st.selectbox(
    "モードを選択してください",
    ["トレーニング", "管理", "履歴"],
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
# 管理モード（必要に応じて拡張）
# ---------------------------------------------------------
elif mode == "管理":
    st.header("⚙ 管理モード")
    st.write("ここに問題追加機能などを配置できます。")

# ---------------------------------------------------------
# 履歴モード
# ---------------------------------------------------------
elif mode == "履歴":
    st.header("📊 履歴")

    rows = load_history()
    st.write(f"最新 {len(rows)} 件を表示")

    for row in rows:
        st.write(f"【{row[5]}】 {row[1]} / {row[2]} → {row[4]}")












