import streamlit as st
import json
import random
import sqlite3
import os
from datetime import datetime

# =========================================
#  絶対パスの設定（history.db の nul 問題対策）
# =========================================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, "history.db")

# =========================================
#  SQLite 初期化（最新5000件だけ残す & correct カラム追加）
# =========================================
def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    # テーブル作成
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

    # correct カラムがない場合に追加（既存DB対応）
    try:
        c.execute("ALTER TABLE history ADD COLUMN correct INTEGER")
    except:
        pass

    # ★ 最新5000件だけ残す
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
#  JSON 読み込み・保存
# =========================================
def load_questions(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def save_questions(path, data):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

# =========================================
#  文型・文法カテゴリのマッピング（最新版）
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
#  ★ サイドバー廃止 → メイン画面に移動
# =========================================
# ★ タイトルをスマホで1行に収めるCSS
st.markdown("""
    <style>
    h1, h2 {
        font-size: 1.6rem !important;
        white-space: nowrap !important;
    }
    </style>
""", unsafe_allow_html=True)

st.title("瞬間英作文アプリ")

mode = st.selectbox("モード選択", ["トレーニング", "苦手問題", "管理", "履歴を見る"])
pattern = st.selectbox("文型・文法を選択", list(FILE_MAP.keys()))
file_path = FILE_MAP[pattern]

# JSON 読み込み
questions = load_questions(file_path)

# =========================================
# ★ 文型・文法を変更したら問題をリセット
# =========================================
if "last_pattern" not in st.session_state:
    st.session_state.last_pattern = pattern

if st.session_state.last_pattern != pattern:
    st.session_state.current = random.choice(questions)
    st.session_state.show_answer = False
    st.session_state.last_pattern = pattern

# =========================================
#  ① トレーニングモード
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
#  ② 苦手問題モード
# =========================================
elif mode == "苦手問題":
    st.title("苦手問題トレーニング（不正解だった問題のみ）")

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
        st.info("苦手問題はありません！（すべて正解しています）")
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
#  ③ 管理モード
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
#  ④ 履歴を見る
# =========================================
else:
    st.title("出題履歴（最新5000件まで保持）")

    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    c.execute("SELECT COUNT(*), SUM(correct) FROM history")
    total, correct = c.fetchone()

    if total and total > 0:
        accuracy = (correct / total) * 100
        st.subheader(f"全体の正答率：{accuracy:.1f}%")
    else:
        st.subheader("まだ正答データがありません。")

    c.execute("SELECT datetime, pattern, jp, en, correct FROM history ORDER BY id DESC")
    rows = c.fetchall()
    conn.close()

    for row in rows:
        dt, pat, jp, en, correct = row
        result = "⭕ 正解" if correct == 1 else "❌ 不正解"
        st.write(f"**{dt}** / {pat} / {result}")
        st.write(f"- JP: {jp}")
        st.write(f"- EN: {en}")
        st.write("---")

    # =========================================
    # ★ 学習の記録（A〜E＋学習時間）
    # =========================================
    st.header("📘 学習の記録")

    # DB 再取得（datetime を日付ごとに集計するため）
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.execute("SELECT datetime, pattern, correct FROM history ORDER BY datetime ASC")
    logs = c.fetchall()
    conn.close()

    if len(logs) == 0:
        st.info("まだ学習データがありません。")
    else:
        # 日別集計用
        daily_count = {}       # A: 日別の学習量
        daily_correct = {}     # B: 日別の正答率
        daily_time = {}        # D: 日別の学習時間（分）

        # カテゴリ別集計用
        category_count = {}    # C: カテゴリ別の学習量
        category_correct = {}  # C: カテゴリ別の正答率

        # 日別の最初と最後の時間を記録
        first_time = {}
        last_time = {}

        for dt, pat, cor in logs:
            date = dt.split(" ")[0]  # YYYY-MM-DD

            # A: 日別の学習量
            daily_count[date] = daily_count.get(date, 0) + 1

            # B: 日別の正答率
            if date not in daily_correct:
                daily_correct[date] = {"correct": 0, "total": 0}
            daily_correct[date]["total"] += 1
            if cor == 1:
                daily_correct[date]["correct"] += 1

            # C: カテゴリ別
            category_count[pat] = category_count.get(pat, 0) + 1
            if pat not in category_correct:
                category_correct[pat] = {"correct": 0, "total": 0}
            category_correct[pat]["total"] += 1
            if cor == 1:
                category_correct[pat]["correct"] += 1

            # D: 日別の学習時間
            if date not in first_time:
                first_time[date] = dt
            last_time[date] = dt

        # 学習時間（分）を算出
        from datetime import datetime as dt2
        for date in first_time:
            t1 = dt2.strptime(first_time[date], "%Y-%m-%d %H:%M:%S")
            t2 = dt2.strptime(last_time[date], "%Y-%m-%d %H:%M:%S")
            minutes = int((t2 - t1).total_seconds() / 60)
            daily_time[date] = minutes

        # =========================================
        # A: 日別の学習量
        # =========================================
        st.subheader("📅 日別の学習量（A）")
        for date, count in daily_count.items():
            st.write(f"- {date}：{count}問")

        # =========================================
        # B: 日別の正答率
        # =========================================
        st.subheader("🎯 日別の正答率（B）")
        for date, data in daily_correct.items():
            acc = (data["correct"] / data["total"]) * 100
            st.write(f"- {date}：{acc:.1f}%")

        # =========================================
        # D: 日別の学習時間
        # =========================================
        st.subheader("⏱ 日別の学習時間（D）")
        for date, minutes in daily_time.items():
            st.write(f"- {date}：{minutes}分")

        # =========================================
        # C: カテゴリ別の学習量・正答率
        # =========================================
        st.subheader("📚 カテゴリ別の学習量・正答率（C）")
        for pat in category_count:
            total = category_correct[pat]["total"]
            cor = category_correct[pat]["correct"]
            acc = (cor / total) * 100
            st.write(f"- {pat}：{total}問（正答率 {acc:.1f}%）")

















