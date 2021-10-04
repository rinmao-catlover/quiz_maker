import streamlit as st
import pandas as pd
import random as rnd
from copy import deepcopy

def load_master_data():
    df = pd.read_csv("data/master.csv", header=None, names=["name", "subject", "volume", "section"])
    tmp = df.groupby("subject")
    df_eitango = tmp.get_group("英単語").set_index("name").drop("subject", axis=1)
    df_eijukugo = tmp.get_group("英熟語").set_index("name").drop("subject", axis=1)
    df_kobuntango = tmp.get_group("古文単語").set_index("name").drop("subject", axis=1)
    return df_eitango, df_eijukugo, df_kobuntango

def create_question_list(book, n, start, end):
    df = pd.read_csv(f"data/word_data/{book}.csv", header=None, names=["word", "meaning"])
    df.index += 1
    if start <= end:
        L = list(range(start, end+1))
    else:
        L = list(range(start, len(df)+1)) + list(range(1, end))
    L = sorted(rnd.sample(L, n))
    question_list = [[i, df["word"].loc[i], df["meaning"].loc[i]] for i in L]
    return question_list

def section_to_number(book, start, end):
    section_df = pd.read_csv(f"data/section_data/{book}.csv", header=None, names=["start", "end"])
    section_df.index += 1
    start = section_df.loc[start]["start"]
    end = section_df.loc[end]["end"]
    return start, end

def create_img(quiz_data, no_num):
    import PIL.Image
    import PIL.ImageDraw
    import PIL.ImageFont

    fontname = "ヒラギノ丸ゴ ProN W4.ttc"
    fontsize = 12
    font = PIL.ImageFont.truetype(fontname, fontsize)

    canvasSize = (500, 800)
    backgroundRGB = (255, 255, 255)
    textRGB = (0, 0, 0)

    img_quiz = PIL.Image.new('RGB', canvasSize, backgroundRGB)
    draw_quiz = PIL.ImageDraw.Draw(img_quiz)

    img_answer = PIL.Image.new('RGB', canvasSize, backgroundRGB)
    draw_answer = PIL.ImageDraw.Draw(img_answer)

    r = 1
    for s in ("英単語", "英熟語", "古文単語"):
        book = quiz_data[s]["book"]
        if book == "なし":
            continue
        question_list = quiz_data[s]["question_list"]
        draw_quiz.text((30, r * 20), f"{book}\n", fill=textRGB, font=font)
        draw_answer.text((30, r * 20), f"{book}\n", fill=textRGB, font=font)
        r += 1
        for i, word, meaning in question_list:
            draw_quiz.text((30, r * 20), f"{'' if no_num else ' '+str(i)} {word}\n", fill=textRGB, font=font)
            draw_answer.text((30, r * 20), f"{' '+str(i)} {meaning}\n", fill=textRGB, font=font)
            r += 1
        r += 1

    return img_quiz, img_answer

col1, col2 = st.columns((2, 1))
col1.markdown("# 小テスト作成くんVer.3.0")
col2.write("<br><br>created by Rin, ANGYM CEO", unsafe_allow_html=True)

st.markdown('***')
with st.expander("-----使用方法------"):
    st.text("単語帳を選択後、出題数・範囲を選び、[小テスト作成]ボタンを押してください。"
            "\n開始点を終了点よりも大きくすることも可能です。"
            "\n"
            "\n※注意点"
            "\n予期せぬバグが起こる可能性があるので自己責任でお願いします。"
            "\n出題数を出題範囲よりも大きくするとエラーになります。"
            "\n出題数が多すぎると画像が適切に作成されません。")

df_eitango, df_eijukugo, df_kobuntango = load_master_data()

# データ格納用
quiz_data = {s:{"book": "なし",
                "num": 10,
                "ranges":[-1, -1],
                "question_list": []}
             for s in ("英単語", "英熟語", "古文単語")}

##### 英単語 #####
st.markdown("### 英単語")
_, col = st.columns((.1, 3))
quiz_data["英単語"]["book"] = col.selectbox(
    "使用する英単語を選んでください",
    ["なし"]+list(df_eitango.index),
)
if quiz_data["英単語"]["book"] != "なし":
    book = quiz_data["英単語"]["book"]
    use_section = False
    if df_eitango.loc[book].section != "F":
        use_section = col.checkbox("章番号を使用する")
    if use_section:
        volume = int(df_eitango.loc[book].section)
    else:
        volume = df_eitango.loc[book].volume

    quiz_data["英単語"]["num"] = col.number_input("英単語の出題数を選んでください", 1, 20, 15)
    start = col.number_input(f"開始点をえらんでくさい(1-{volume})",
                    1, volume, 1)
    end = col.number_input(f"終了点を選んでください(1-{volume})",
                    1, volume, volume)
    if use_section:
        start, end = section_to_number(book, start, end)
    quiz_data["英単語"]["ranges"] = [start, end]

##### 英熟語 #####
st.markdown("### 英熟語")
_, col = st.columns((.1, 3))
quiz_data["英熟語"]["book"] = col.selectbox(
    "使用する英熟語を選んでください",
    ["なし"]+list(df_eijukugo.index),
)
if quiz_data["英熟語"]["book"] != "なし":
    use_section = False
    book = quiz_data["英熟語"]["book"]
    if df_eijukugo.loc[book].section != "F":
        use_section = col.checkbox("章番号を使用する")
    if use_section:
        volume = int(df_eijukugo.loc[book].section)
    else:
        volume = df_eijukugo.loc[book].volume
    quiz_data["英熟語"]["num"] = col.number_input("英熟語の出題数を選んでください", 1, 20, 15)
    start = col.number_input(f"開始点をえらんでくさい(1-{volume})",
                    1, volume, 1)
    end = col.number_input(f"終了点を選んでください(1-{volume})",
                    1, volume, volume)
    if use_section:
        start, end = section_to_number(book, start, end)
    quiz_data["英熟語"]["ranges"] = [start, end]

##### 古文単語 #####
st.markdown("### 古文単語")
_, col = st.columns((.1, 3))
quiz_data["古文単語"]["book"] = col.selectbox(
    "使用する古文単語を選んでください",
    ["なし"]+list(df_kobuntango.index),
)
if quiz_data["古文単語"]["book"] != "なし":
    use_section = False
    book = quiz_data["古文単語"]["book"]
    if df_kobuntango.loc[book].section != "F":
        use_section = col.checkbox("章番号を使用する")
    if use_section:
        volume = int(df_kobuntango.loc[book].section)
    else:
        volume = df_kobuntango.loc[book].volume

    quiz_data["古文単語"]["num"] = col.number_input("古文単語の出題数を選んでください", 1, 20, 15)
    start = col.number_input(f"開始点をえらんでくさい(1-{volume})",
                    1, volume, 1)
    end = col.number_input(f"終了点を選んでください(1-{volume})",
                    1, volume, volume)
    if use_section:
        start, end = section_to_number(book, start, end)
    quiz_data["古文単語"]["ranges"] = [start, end]



st.write("#### オプション", unsafe_allow_html=True)
_, col = st.columns((.1, 3))
shuffle = col.checkbox("問題をシャッフルする")
no_num = col.checkbox("問題番号を非表示にする")
create = st.button("小テスト作成")

st.markdown('***')
##### 作成 #####
if create:
    st.success("小テストを作成しました！！！")
    for s in ("英単語", "英熟語", "古文単語"):
        if quiz_data[s]["book"] != "なし":
            question_list = create_question_list(quiz_data[s]["book"],
                                                 quiz_data[s]["num"],
                                                 *quiz_data[s]["ranges"])
            quiz_data[s]["question_list"] = deepcopy(question_list)
            if shuffle:
                rnd.shuffle(quiz_data[s]["question_list"])


    # for s in ("英単語", "英熟語", "古文単語"):
    #     book = quiz_data[s]["book"]
    #     question_list = quiz_data[s]["question_list"]
    #     if book != "なし":
    #         st.write(book)
    #         for i, word, meaning in question_list:
    #             st.write(f"{i} {word} {meaning}")

    st.text("\n")
    st.text("\n")
    st.markdown("### 出題番号")
    if quiz_data["英単語"]["book"] != "なし":
        out = [i for i, _, _ in quiz_data["英単語"]["question_list"]]
        out.sort()
        out = [str(i) for i in out]
        out = ", ".join(out)
        st.text_input(f"英単語({quiz_data['英単語']['book']})", out)
    if quiz_data["英熟語"]["book"] != "なし":
        out = [i for i, _, _ in quiz_data["英単語"]["question_list"]]
        out.sort()
        out = [str(i) for i in out]
        out = ", ".join(out)
        st.text_input(f"英熟語({quiz_data['英熟語']['book']})", out)
    if quiz_data["古文単語"]["book"] != "なし":
        out = [i for i, _, _ in quiz_data["古文単語"]["question_list"]]
        out.sort()
        out = [str(i) for i in out]
        out = ", ".join(out)
        st.text_input(f"古文単語({quiz_data['古文単語']['book']})", out)

    img_quiz, img_answer = create_img(quiz_data, no_num=no_num)

    col1, col2 = st.columns(2)
    with col1:
        st.markdown("### 問題")
        st.image(img_quiz, use_column_width=True)
    with col2:
        st.markdown("### 解答")
        st.image(img_answer, use_column_width=True)
