import streamlit as st
from PyPDF2 import PdfReader
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from gtts import gTTS
import requests
import re
import time
import os

API_KEY = "AIzaSyDsXwoXa2vm3ZzNwIs__3WAtTZfts2SoUs"

st.set_page_config(page_title="AI Study Assistant", page_icon="🤖", layout="wide")

# ================= STYLE =================
st.markdown("""
<style>
body {background-color: #0E1117;}
h1,h2,h3 {color:#00ADB5;}
</style>
""", unsafe_allow_html=True)

# ================= SIDEBAR =================
with st.sidebar:
    st.title("📂 Control Panel")
    pdfs = st.file_uploader("Upload PDFs", type="pdf", accept_multiple_files=True)

    if st.button("Clear Chat"):
        st.session_state.messages = []

# ================= SESSION =================
if "messages" not in st.session_state:
    st.session_state.messages = []
if "pdf_text" not in st.session_state:
    st.session_state.pdf_text = ""
if "score" not in st.session_state:
    st.session_state.score = 0
if "total" not in st.session_state:
    st.session_state.total = 0

# ================= PDF LOAD =================
if pdfs:
    text = ""
    for pdf in pdfs:
        reader = PdfReader(pdf)
        for page in reader.pages:
            if page.extract_text():
                text += page.extract_text()

    st.session_state.pdf_text = re.sub(r'\s+', ' ', text)

# ================= CHAT =================
st.title("🤖 AI Study Assistant")

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

def speak(text):
    tts = gTTS(text)
    tts.save("out.mp3")
    return "out.mp3"

question = st.chat_input("Ask from PDF")

if question:
    st.session_state.messages.append({"role":"user","content":question})

    sentences = re.split(r'(?<=[.!?]) +', st.session_state.pdf_text)

    vect = TfidfVectorizer(stop_words='english')
    X = vect.fit_transform(sentences + [question])

    sim = cosine_similarity(X[-1], X[:-1])[0]
    ans = sentences[sim.argmax()] if len(sentences)>0 else "Upload PDF"

    st.session_state.messages.append({"role":"assistant","content":ans})

    with st.chat_message("assistant"):
        st.write(ans)
        if st.button("🔊 Speak"):
            st.audio(speak(ans))

# ================= QUIZ =================
st.markdown("---")
st.subheader("📝 Quiz")

difficulty = st.selectbox("Difficulty",["Easy","Medium","Hard"])
quiz_type = st.selectbox("Type",["MCQ","True/False","Fill"])

def generate_quiz(text):
    s = text.split(".")
    num = 3 if difficulty=="Easy" else 5 if difficulty=="Medium" else 8
    return s[:num]

if st.button("Generate Quiz"):
    st.session_state.score = 0
    st.session_state.total = 0

    qs = generate_quiz(st.session_state.pdf_text)

    for i,q in enumerate(qs):
        if len(q.strip())<20:
            continue

        st.write(f"Q{i+1}: {q}")

        if quiz_type=="MCQ":
            st.radio("Answer",["A","B","C","D"],key=i)
        elif quiz_type=="True/False":
            st.radio("Answer",["True","False"],key=i)
        else:
            st.write("Fill:",q[:40],"_____")

        if st.button(f"Submit {i}", key=f"s{i}"):
            st.session_state.total += 1

    st.write(f"Score: {st.session_state.score}/{st.session_state.total}")

# ================= FLASHCARDS =================
st.markdown("---")
st.subheader("📚 Flashcards")

if st.button("Generate Flashcards"):
    for i,s in enumerate(st.session_state.pdf_text.split(".")[:5]):
        if len(s.strip())<20:
            continue

        st.write(f"Card {i+1}")
        st.write("Q:",s[:40])
        st.write("A:",s)

        if st.button(f"🔊 {i}", key=f"a{i}"):
            st.audio(speak(s))

# ================= YOUTUBE =================
st.markdown("---")
st.subheader("🎥 Learn from Videos")

topic = st.text_input("Enter topic")

def search_youtube(query):
    url = f"https://www.googleapis.com/youtube/v3/search?part=snippet&q={query}&key={API_KEY}&maxResults=3&type=video"
    res = requests.get(url).json()

    videos = []
    for item in res.get("items", []):
        vid = item["id"]["videoId"]
        videos.append(f"https://youtube.com/watch?v={vid}")
    return videos

if st.button("Search Videos"):
    vids = search_youtube(topic)
    for v in vids:
        st.video(v)