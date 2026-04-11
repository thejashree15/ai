import streamlit as st
from PyPDF2 import PdfReader
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from gtts import gTTS
from dotenv import load_dotenv
import requests
import re
import time
import os

# ================== ENV ==================
load_dotenv()
API_KEY = os.getenv("YOUTUBE_API_KEY")

# ================== PAGE ==================
st.set_page_config(page_title="AI Study Assistant", page_icon="🤖", layout="wide")

st.markdown("""
<style>
body { background-color:#0E1117; }
h1,h2,h3 { color:#00ADB5; }
</style>
""", unsafe_allow_html=True)

# ================== SIDEBAR ==================
with st.sidebar:
    st.header("📂 Control Panel")
    pdfs = st.file_uploader("Upload PDFs", type="pdf", accept_multiple_files=True)

    if st.button("🧹 Clear Chat"):
        st.session_state.messages = []
        st.session_state.pdf_text = ""
        st.session_state.score = 0
        st.session_state.total = 0
        st.rerun()

# ================== SESSION STATE ==================
if "messages" not in st.session_state:
    st.session_state.messages = []

if "pdf_text" not in st.session_state:
    st.session_state.pdf_text = ""

if "score" not in st.session_state:
    st.session_state.score = 0

if "total" not in st.session_state:
    st.session_state.total = 0

# ================== LOAD PDF ==================
if pdfs:
    text = ""
    for pdf in pdfs:
        reader = PdfReader(pdf)
        for page in reader.pages:
            if page.extract_text():
                text += page.extract_text()

    st.session_state.pdf_text = re.sub(r"\s+", " ", text)
    st.success("PDFs loaded successfully ✔")

# ================== TITLE ==================
st.title("🤖 AI Study Assistant")

# ================== CHAT ==================
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

def speak(text):
    tts = gTTS(text)
    tts.save("speech.mp3")
    return "speech.mp3"

question = st.chat_input("Ask from your PDFs")

if question:
    st.session_state.messages.append({"role": "user", "content": question})

    if not st.session_state.pdf_text:
        answer = "⚠ Upload a PDF first."
    else:
        sentences = re.split(r"(?<=[.!?]) +", st.session_state.pdf_text)

        vectorizer = TfidfVectorizer(stop_words="english")
        X = vectorizer.fit_transform(sentences + [question])
        similarity = cosine_similarity(X[-1], X[:-1])[0]

        idx = similarity.argmax()
        answer = sentences[idx]

    st.session_state.messages.append({"role": "assistant", "content": answer})

    with st.chat_message("assistant"):
        st.write(answer)
        if st.button("🔊 Listen"):
            st.audio(speak(answer))

# ================== QUIZ ==================
st.markdown("---")
st.subheader("📝 Quiz Generator")

difficulty = st.selectbox("Difficulty", ["Easy", "Medium", "Hard"])
quiz_type = st.selectbox("Type", ["MCQ", "True/False", "Fill"])

def generate_quiz(text):
    sentences = text.split(".")
    count = 3 if difficulty == "Easy" else 5 if difficulty == "Medium" else 8
    return sentences[:count]

if st.button("Generate Quiz"):
    questions = generate_quiz(st.session_state.pdf_text)

    for i, q in enumerate(questions):
        if len(q.strip()) < 20:
            continue

        st.write(f"Q{i+1}: {q}")

        if quiz_type == "MCQ":
            st.radio("Choose:", ["A", "B", "C", "D"], key=f"q{i}")
        elif quiz_type == "True/False":
            st.radio("Choose:", ["True", "False"], key=f"q{i}")
        else:
            st.text_input("Answer:", key=f"q{i}")

        if st.button(f"Submit {i+1}", key=f"s{i}"):
            st.session_state.total += 1
            st.session_state.score += 1

    st.write(f"Score: {st.session_state.score}/{st.session_state.total}")

# ================== FLASHCARDS ==================
st.markdown("---")
st.subheader("📚 Flashcards")

if st.button("Generate Flashcards"):
    for i, s in enumerate(st.session_state.pdf_text.split(".")[:5]):
        if len(s.strip()) < 20:
            continue

        st.write(f"Card {i+1}")
        st.write("Q:", s[:40] + " ...")
        st.write("A:", s)

        if st.button(f"🔊 Read {i+1}", key=f"f{i}"):
            st.audio(speak(s))

# ================== YOUTUBE ==================
st.markdown("---")
st.subheader("🎥 Learn From YouTube")

topic = st.text_input("Enter topic")

def search_youtube(q):
    url = (
        "https://www.googleapis.com/youtube/v3/search"
        f"?part=snippet&q={q}&type=video&maxResults=3&key={API_KEY}"
    )
    data = requests.get(url).json()

    videos = []
    for item in data.get("items", []):
        vid = item["id"]["videoId"]
        videos.append(f"https://www.youtube.com/watch?v={vid}")
    return videos

if st.button("Search Videos"):
    videos = search_youtube(topic)
    for v in videos:
        st.video(v)