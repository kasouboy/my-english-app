import streamlit as st
import json
import random
import sqlite3
import os
from datetime import datetime

# =========================================
#  絶対パスの設定
# =========================================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "history.db")

# =========================================
#  datetime パーサー（ミリ秒あり/なし対応）
# =========================================
def parse_datetime(dt_str):
    try:
        return datetime.strptime(dt_str, "%Y-%m-%d %H:%M:%S.%f")
    except:
        pass
    try:
        return datetime.strptime(dt_str, "%Y-%m-%d %H:%M:%S")
    except:
        pass
    return None

# =========================================
#  SQLite 初期化
# =========================================
def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    c.execute("""
        CREATE TABLE IF NOT EXISTS history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            datetime TEXT,
            pattern TEXT,
            jp TEXT,
            en TEXT,
            correct INTEGER
        )
    """)

    try:
        c.execute("ALTER TABLE history ADD COLUMN correct INTEGER")
    except:
        pass

    c.execute("""
        DELETE FROM history
        WHERE id NOT IN (
            SELECT id FROM history ORDER BY id DESC LIMIT 5000
        )
    """)

    conn.commit()
    conn.close()

def write_history(pattern, jp, en, correct):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute(
        "INSERT INTO history (datetime, pattern, jp, en, correct) VALUES (?, ?, ?, ?, ?)",
        (datetime.now(), pattern, jp, en, correct)
    )
    conn.commit()
    conn.close()

# =========================================
#  JSON 読み込み
# =========================================
def load_questions(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def save_questions(path, data):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

# =========================================
#  FILE MAP
# =========================================
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

# DB 初期化
init_db()

# =========================================
#  タイトルをスマホで1行に
# =========================================
st.markdown("""
    <style>
    h1, h2 {
        font-size: 1.6rem !important;
        white-space: nowrap !important;
    }
    </style>
""", unsafe_allow_html=True)

# =========================================
#  UI
# =========================================
st.title("瞬間英作文アプリ")

mode = st.selectbox("モード選択", ["トレーニング", "苦手問題", "管理", "履歴を見る"])
pattern = st.selectbox("文型・文法を選択", list(FILE_MAP.keys()))
file_path = FILE_MAP[pattern]
questions = load_questions(file_path)

# =========================================
#  文型変更で問題リセット
# =========================================
if "last_pattern" not in st.session_state:
    st.session_state.last_pattern = pattern

if st.session_state.last_pattern != pattern:
    st.session_state.current = random.choice(questions)
    st.session_state.show_answer = False
    st.session_state.last_pattern = pattern

# =========================================
#  トレーニング
# =========================================
if mode == "トレーニング":
    st.header("瞬間英作文トレーニング")

    if "current" not in st.session_state:
        st.session_state.current = random.choice(questions)
        st.session_state.show_answer = False

    jp = st.session_state.current["jp"]
    en = st.session_state.current["en"]

    st.subheader("日本語の文")
    st.write(jp)

    if st.button("答えを見る"):
        st.session_state.show_answer = True

    if st.session_state.show_answer:
        st.write("### 英語の答え")
        st.success(en)

        col1, col2 = st.columns(2)
        with col1:
            if st.button("できた！"):
                write_history(pattern, jp, en, 1)
                st.session_state.current = random.choice(questions)
                st.session_state.show_answer = False
                st.rerun()

        with col2:
            if st.button("できなかった…"):
                write_history(pattern, jp, en, 0)
                st.session_state.current = random.choice(questions)
                st.session_state.show_answer = False
                st.rerun()

# =========================================
#  苦手問題
# =========================================
elif mode == "苦手問題":
    st.title("苦手問題トレーニング（不正解のみ）")

    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("""
        SELECT pattern, jp, en FROM history
        WHERE correct = 0
        ORDER BY id DESC
    """)
    wrong_rows = c.fetchall()
    conn.close()

    if len(wrong_rows) == 0:
        st.info("苦手問題はありません！")
    else:
        pattern, jp, en = random.choice(wrong_rows)

        st.subheader(f"カテゴリ：{pattern}")
        st.write("### 日本語の文")
        st.write(jp)

        if st.button("答えを見る"):
            st.session_state.show_answer = True

        if st.session_state.get("show_answer", False):
            st.write("### 英語の答え")
            st.success(en)

            col1, col2 = st.columns(2)
            with col1:
                if st.button("できた！"):
                    write_history(pattern, jp, en, 1)
                    st.session_state.show_answer = False
                    st.rerun()

            with col2:
                if st.button("できなかった…"):
                    write_history(pattern, jp, en, 0)
                    st.session_state.show_answer = False
                    st.rerun()

# =========================================
#  管理
# =========================================
elif mode == "管理":
    st.title("問題管理画面")

    st.write(f"現在のカテゴリ：**{pattern}**")
    st.write(f"ファイル：**{file_path}**")

    st.subheader("新しい問題を追加")

    new_jp = st.text_area("日本語文")
    new_en = st.text_area("英語文")

    if st.button("追加する"):
        if new_jp.strip() == "" or new_en.strip() == "":
            st.error("日本語と英語の両方を入力してください")
        else:
            questions.append({"jp": new_jp, "en": new_en})
            save_questions(file_path, questions)
            st.success("問題を追加しました！")
            st.rerun()

    st.write("---")
    st.subheader("現在の問題一覧")

    for q in questions:
        st.write(f"- **JP:** {q['jp']} / **EN:** {q['en']}")

# =========================================
#  履歴 + 学習記録 + 棒グラフ
# =========================================
else:
    st.title("学習データ")

    # -------------------------
    # 履歴データ取得
    # -------------------------
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT datetime, pattern, jp, en, correct FROM history ORDER BY id DESC")
    rows = c.fetchall()
    conn.close()

    # -------------------------
    # 履歴は折りたたみ
    # -------------------------
    with st.expander("▼ 出題履歴（タップで開く）"):
        for row in rows:
            dt, pat, jp, en, correct = row
            result = "⭕ 正解" if correct == 1 else "❌ 不正解"
            st.write(f"**{dt}** / {pat} / {result}")
            st.write(f"- JP: {jp}")
            st.write(f"- EN: {en}")
            st.write("---")

    # -------------------------
    # 学習記録用データ取得
    # -------------------------
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT datetime, pattern, correct FROM history ORDER BY datetime ASC")
    logs = c.fetchall()
    conn.close()

    if len(logs) == 0:
        st.info("まだ学習データがありません。")
    else:
        daily_count = {}
        daily_correct = {}
        daily_time = {}
        category_count = {}
        category_correct = {}
        first_time = {}
        last_time = {}

        for dt, pat, cor in logs:
            date = dt.split(" ")[0]

            daily_count[date] = daily_count.get(date, 0) + 1

            if date not in daily_correct:
                daily_correct[date] = {"correct": 0, "total": 0}
            daily_correct[date]["total"] += 1
            if cor == 1:
                daily_correct[date]["correct"] += 1

            category_count[pat] = category_count.get(pat, 0) + 1
            if pat not in category_correct:
                category_correct[pat] = {"correct": 0, "total": 0}
            category_correct[pat]["total"] += 1
            if cor == 1:
                category_correct[pat]["correct"] += 1

            if date not in first_time:
                first_time[date] = dt
            last_time[date] = dt

        for date in first_time:
            t1 = parse_datetime(first_time[date])
            t2 = parse_datetime(last_time[date])
            if t1 and t2:
                minutes = int((t2 - t1).total_seconds() / 60)
            else:
                minutes = 0
            daily_time[date] = minutes

        # -------------------------
        # 棒グラフを最初に表示
        # -------------------------
        import pandas as pd

        st.header("📊 棒グラフで見る学習記録")

        df_daily_count = pd.DataFrame({
            "date": list(daily_count.keys()),
            "count": list(daily_count.values())
        }).sort_values("date")
        st.write("### 日別の学習量（A）")
        st.bar_chart(df_daily_count, x="date", y="count")

        df_daily_acc = pd.DataFrame({
            "date": list(daily_correct.keys()),
            "accuracy": [
                (v["correct"] / v["total"]) * 100 for v in daily_correct.values()
            ]
        }).sort_values("date")
        st.write("### 日別の正答率（B）")
        st.bar_chart(df_daily_acc, x="date", y="accuracy")

        df_cat_count = pd.DataFrame({
            "category": list(category_count.keys()),
            "count": list(category_count.values())
        }).sort_values("count", ascending=False)
        st.write("### カテゴリ別の学習量（C）")
        st.bar_chart(df_cat_count, x="category", y="count")

        # -------------------------
        # 学習記録（テキスト）
        # -------------------------
        st.header("📘 学習の記録")

        st.subheader("📅 日別の学習量（A）")
        for date, count in daily_count.items():
            st.write(f"- {date}：{count}問")

        st.subheader("🎯 日別の正答率（B）")
        for date, data in daily_correct.items():
            acc = (data["correct"] / data["total"]) * 100
            st.write(f"- {date}：{acc:.1f}%")

        st.subheader("⏱ 日別の学習時間（D）")
        for date, minutes in daily_time.items():
            st.write(f"- {date}：{minutes}分")

        st.subheader("📚 カテゴリ別の学習量・正答率（C）")
        for pat in category_count:
            total = category_correct[pat]["total"]
            cor = category_correct[pat]["correct"]
            acc = (cor / total) * 100
            st.write(f"- {pat}：{total}問（正答率 {acc:.1f}%）")



















