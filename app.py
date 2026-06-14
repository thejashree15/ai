import streamlit as st
<<<<<<< HEAD

# ================== PAGE CONFIG ==================
st.set_page_config(
    page_title="AI Study Assistant",
    page_icon="🤖",
    layout="wide"
)

# ================== IMPORTS ==================
from dotenv import load_dotenv
load_dotenv()

from PyPDF2 import PdfReader
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sentence_transformers import SentenceTransformer
from gtts import gTTS
from openai import OpenAI

import faiss
import numpy as np
import requests
import os
import re

# ================== OPENROUTER ==================

OPENROUTER_API_KEY = st.secrets["OPENROUTER_API_KEY"]

client = OpenAI(
    api_key=OPENROUTER_API_KEY,
    base_url="https://openrouter.ai/api/v1"
)

# ================== LOAD MODEL ==================

@st.cache_resource
def load_model():
    return SentenceTransformer("all-MiniLM-L6-v2")

with st.spinner("🔄 Loading AI model..."):
    model = load_model()

# ================== TITLE ==================

st.title("🤖 AI Study Assistant")
st.write("Upload PDFs → Ask Questions → Generate Notes, Quiz & Flashcards")

# ================== SESSION STATE ==================

=======
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
>>>>>>> e56a1348493cbddb0ae653b5bb3b40a5648b8c86
if "messages" not in st.session_state:
    st.session_state.messages = []

if "pdf_text" not in st.session_state:
    st.session_state.pdf_text = ""

<<<<<<< HEAD
if "pdf_loaded" not in st.session_state:
    st.session_state.pdf_loaded = False

# ================== SIDEBAR ==================

with st.sidebar:

    st.header("📂 Control Panel")

    pdfs = st.file_uploader(
        "Upload PDFs",
        type="pdf",
        accept_multiple_files=True
    )

    if st.button("🧹 Clear Chat"):

        st.session_state.messages = []
        st.session_state.pdf_text = ""
        st.session_state.pdf_loaded = False

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

# ================== OPENROUTER AI ==================

def ask_ai(prompt):

    try:

        response = client.chat.completions.create(
            model="deepseek/deepseek-chat",
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        )

        return response.choices[0].message.content

    except Exception as e:

        return f"Error: {e}"

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

        st.error("❌ PDF has no readable text")

    else:

        st.session_state.pdf_text = text

        st.session_state.index, st.session_state.sentences = create_faiss_index(text)

        st.session_state.pdf_loaded = True

        st.success("✅ PDF Loaded Successfully")

# ================== SEARCH MODE ==================

mode = st.selectbox(
    "Search Mode",
    ["TF-IDF", "FAISS", "Hybrid"]
)

# ================== CHAT ==================

st.markdown("---")
st.markdown("## 💬 Chat with PDF")

for msg in st.session_state.messages:

    with st.chat_message(msg["role"]):

        st.write(msg["content"])
=======
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
>>>>>>> e56a1348493cbddb0ae653b5bb3b40a5648b8c86

question = st.chat_input("Ask from your PDFs")

if question:
<<<<<<< HEAD

    st.session_state.messages.append(
        {
            "role": "user",
            "content": question
        }
    )

    if not st.session_state.pdf_loaded:

        answer = "⚠ Upload PDF first"

    else:

        if mode == "TF-IDF":

            answer = get_tfidf_answer(
                st.session_state.pdf_text,
                question
            )

        elif mode == "FAISS":

            answer = get_faiss_answer(question)

        else:

            answer = (
                get_tfidf_answer(
                    st.session_state.pdf_text,
                    question
                )
                + "\n\n" +
                get_faiss_answer(question)
            )

    st.session_state.messages.append(
        {
            "role": "assistant",
            "content": answer
        }
    )

    with st.chat_message("assistant"):

        st.write(answer)

        if st.button("🔊 Listen", key=str(len(st.session_state.messages))):

            st.audio(speak(answer))

# ================== AI NOTES ==================

st.markdown("---")
st.markdown("## 🧾 AI Notes")

if st.button("Generate Notes"):

    if not st.session_state.pdf_loaded:

        st.warning("Upload PDF first")

    else:

        with st.spinner("Generating Notes..."):

            prompt = f"""
            Generate clean study notes from this content.
            Use simple bullet points.

            Content:
            {st.session_state.pdf_text[:4000]}
            """

            notes = ask_ai(prompt)

        st.write(notes)

# ================== AI QUIZ ==================

st.markdown("---")
st.markdown("## 📝 AI Quiz")

difficulty = st.selectbox(
    "Difficulty",
    ["Easy", "Medium", "Hard"]
)

if st.button("Generate Quiz"):

    if not st.session_state.pdf_loaded:

        st.warning("Upload PDF first")

    else:

        with st.spinner("Generating Quiz..."):

            prompt = f"""
            Generate a {difficulty} multiple choice quiz.

            Create:
            - Questions
            - 4 options
            - Correct answer

            Content:
            {st.session_state.pdf_text[:4000]}
            """

            quiz = ask_ai(prompt)

        st.write(quiz)

# ================== FLASHCARDS ==================

st.markdown("---")
st.markdown("## 📚 AI Flashcards")

if st.button("Generate Flashcards"):

    if not st.session_state.pdf_loaded:

        st.warning("Upload PDF first")

    else:

        with st.spinner("Generating Flashcards..."):

            prompt = f"""
            Create 5 flashcards.

            Format:
            Question:
            Answer:

            Content:
            {st.session_state.pdf_text[:4000]}
            """

            flashcards = ask_ai(prompt)

        st.write(flashcards)

# ================== SUMMARY ==================

st.markdown("---")
st.markdown("## 📄 AI Summary")

if st.button("Generate Summary"):

    if not st.session_state.pdf_loaded:

        st.warning("Upload PDF first")

    else:

        with st.spinner("Generating Summary..."):

            prompt = f"""
            Summarize this study material in simple language.

            Content:
            {st.session_state.pdf_text[:4000]}
            """

            summary = ask_ai(prompt)

        st.write(summary)

# ================== YOUTUBE ==================

st.markdown("---")
st.markdown("## 🎥 Learn From YouTube")

topic = st.text_input("Enter topic")

def search_youtube(query):

    API_KEY = st.secrets["YOUTUBE_API_KEY"]

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

        return []

    data = response.json()

    videos = []

    for item in data.get("items", []):

        if "videoId" in item["id"]:

            vid = item["id"]["videoId"]

            videos.append(
                f"https://www.youtube.com/watch?v={vid}"
            )

    return videos

if st.button("Search Videos"):

    if not topic:

        st.warning("Enter topic")

    else:

        with st.spinner("Searching videos..."):

            vids = search_youtube(topic)

        if vids:

            for v in vids:

                st.video(v)

        else:

            st.warning("No videos found")

# ================== FOOTER ==================

st.markdown("---")
st.caption("🚀 Built with Streamlit + OpenRouter + FAISS")
=======
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
>>>>>>> e56a1348493cbddb0ae653b5bb3b40a5648b8c86
