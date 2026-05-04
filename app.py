import streamlit as st

# ================== PAGE CONFIG (FIRST LINE) ==================
st.set_page_config(page_title="AI Study Assistant", page_icon="🤖", layout="wide")

# ================== IMPORTS ==================
from dotenv import load_dotenv
load_dotenv()

from PyPDF2 import PdfReader
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sentence_transformers import SentenceTransformer
from gtts import gTTS
import faiss
import numpy as np
import requests
import os
import re
import random

# ================== LOAD MODEL ==================
@st.cache_resource
def load_model():
    return SentenceTransformer("all-MiniLM-L6-v2")

with st.spinner("🔄 Loading AI model..."):
    model = load_model()

# ================== TITLE ==================
st.title("🤖 AI Study Assistant")

# ================== SESSION ==================
if "messages" not in st.session_state:
    st.session_state.messages = []

if "pdf_text" not in st.session_state:
    st.session_state.pdf_text = ""

if "pdf_loaded" not in st.session_state:
    st.session_state.pdf_loaded = False

if "score" not in st.session_state:
    st.session_state.score = 0

if "total" not in st.session_state:
    st.session_state.total = 0

# ================== SIDEBAR ==================
with st.sidebar:
    st.header("📂 Control Panel")
    pdfs = st.file_uploader("Upload PDFs", type="pdf", accept_multiple_files=True)

    if st.button("🧹 Clear Chat"):
        st.session_state.messages = []
        st.session_state.pdf_text = ""
        st.session_state.pdf_loaded = False
        st.session_state.score = 0
        st.session_state.total = 0
        st.rerun()

# ================== AUDIO ==================
def speak(text):
    tts = gTTS(text)
    tts.save("speech.mp3")
    return "speech.mp3"

# ================== TF-IDF ==================
def get_tfidf_answer(text, question):
    sentences = re.split(r"(?<=[.!?]) +", text)
    vectorizer = TfidfVectorizer(stop_words="english")
    X = vectorizer.fit_transform(sentences + [question])
    similarity = cosine_similarity(X[-1], X[:-1])[0]
    top = similarity.argsort()[-3:][::-1]
    return " ".join([sentences[i] for i in top])

# ================== FAISS ==================
def create_faiss_index(text):
    sentences = re.split(r"(?<=[.!?]) +", text)
    embeddings = model.encode(sentences)
    index = faiss.IndexFlatL2(embeddings.shape[1])
    index.add(np.array(embeddings))
    return index, sentences

def get_faiss_answer(question):
    q_vec = model.encode([question])
    D, I = st.session_state.index.search(np.array(q_vec), k=3)
    return " ".join([st.session_state.sentences[i] for i in I[0]])

# ================== LOAD PDF ==================
if pdfs:
    st.session_state.pdf_loaded = False

if pdfs and not st.session_state.pdf_loaded:
    text = ""

    for pdf in pdfs:
        reader = PdfReader(pdf)
        for page in reader.pages:
            content = page.extract_text()
            if content:
                text += content

    text = re.sub(r"\s+", " ", text)

    if len(text.strip()) == 0:
        st.error("❌ PDF has no readable text (scanned)")
    else:
        st.session_state.pdf_text = text
        st.session_state.index, st.session_state.sentences = create_faiss_index(text)
        st.session_state.pdf_loaded = True
        st.success("✅ PDF Loaded Successfully")

# ================== MODE ==================
mode = st.selectbox("Search Mode", ["TF-IDF", "FAISS", "Hybrid"])

# ================== CHAT ==================
st.markdown("## 💬 Ask Questions")

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])

question = st.chat_input("Ask from your PDFs")

if question:
    st.session_state.messages.append({"role": "user", "content": question})

    if not st.session_state.pdf_loaded:
        answer = "⚠ Upload PDF first"
    else:
        if mode == "TF-IDF":
            answer = get_tfidf_answer(st.session_state.pdf_text, question)
        elif mode == "FAISS":
            answer = get_faiss_answer(question)
        else:
            answer = get_tfidf_answer(st.session_state.pdf_text, question) + "\n\n" + get_faiss_answer(question)

    st.session_state.messages.append({"role": "assistant", "content": answer})

    with st.chat_message("assistant"):
        st.write(answer)

        if st.button("🔊 Listen", key=str(len(st.session_state.messages))):
            st.audio(speak(answer))

# ================== QUIZ ==================
st.markdown("---")
st.markdown("## 📝 Practice Quiz")

difficulty = st.selectbox("Difficulty", ["Easy", "Medium", "Hard"])

def generate_quiz(text):
    sentences = [s.strip() for s in text.split(".") if len(s.strip()) > 40]
    if not sentences:
        return []

    count = {"Easy":3,"Medium":5,"Hard":8}[difficulty]
    selected = random.sample(sentences, min(count, len(sentences)))

    quiz = []
    for s in selected:
        words = s.split()
        if len(words) < 6:
            continue

        ans = words[len(words)//2]
        ques = s.replace(ans, "_____")

        options = list(set(words[:10]))
        if ans not in options:
            options.append(ans)

        options = options[:4]
        random.shuffle(options)

        quiz.append({"q": ques, "o": options, "a": ans})

    return quiz

if st.button("Generate Quiz"):
    if not st.session_state.pdf_loaded:
        st.warning("Upload PDF first")
    else:
        quiz = generate_quiz(st.session_state.pdf_text)

        for i, q in enumerate(quiz):
            st.write(f"Q{i+1}: {q['q']}")
            user = st.radio("Choose:", q["o"], key=f"q{i}")

            if st.button(f"Submit {i}", key=f"s{i}"):
                st.session_state.total += 1
                if user == q["a"]:
                    st.success("Correct")
                    st.session_state.score += 1
                else:
                    st.error(f"Wrong. Answer: {q['a']}")

        st.write(f"Score: {st.session_state.score}/{st.session_state.total}")

# ================== FLASHCARDS ==================
st.markdown("---")
st.markdown("## 📚 Flashcards")

if st.button("Generate Flashcards"):
    if st.session_state.pdf_loaded:
        for i, s in enumerate(st.session_state.pdf_text.split(".")[:5]):
            if len(s.strip()) > 30:
                st.write(f"Card {i+1}")
                st.write("Q:", s[:60])
                st.write("A:", s)

# ================== NOTES ==================
st.markdown("---")
st.markdown("## 🧾 Notes")

if st.button("Generate Notes"):
    if st.session_state.pdf_loaded:
        for s in st.session_state.pdf_text.split(".")[:10]:
            if len(s.strip()) > 30:
                st.write("-", s.strip())

# ================== YOUTUBE ==================
st.markdown("---")
st.markdown("## 🎥 Learn From YouTube")

topic = st.text_input("Enter topic")

def search_youtube(query):
    API_KEY = os.getenv("YOUTUBE_API_KEY")

    if not API_KEY:
        st.error("❌ API key not found")
        return []

    url = "https://www.googleapis.com/youtube/v3/search"

    params = {
        "part": "snippet",
        "q": query,
        "type": "video",
        "maxResults": 3,
        "key": API_KEY
    }

    response = requests.get(url, params=params)

    if response.status_code != 200:
        st.error("❌ API error")
        return []

    data = response.json()

    videos = []
    for item in data.get("items", []):
        if "videoId" in item["id"]:
            vid = item["id"]["videoId"]
            videos.append(f"https://www.youtube.com/watch?v={vid}")

    return videos

if st.button("Search Videos"):
    if not topic:
        st.warning("Enter topic")
    else:
        vids = search_youtube(topic)

        if vids:
            for v in vids:
                st.video(v)
        else:
            st.warning("No videos found")