import streamlit as st
from dotenv import load_dotenv
from PyPDF2 import PdfReader
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sentence_transformers import SentenceTransformer
from gtts import gTTS
from openai import OpenAI
import faiss
import numpy as np
import requests
import re

# ================= PAGE CONFIG =================
st.set_page_config(
    page_title="AI Study Assistant",
    page_icon="🤖",
    layout="wide"
)

# ================= ENV =================
load_dotenv()

OPENROUTER_API_KEY = st.secrets["OPENROUTER_API_KEY"]
YOUTUBE_API_KEY = st.secrets["YOUTUBE_API_KEY"]

client = OpenAI(
    api_key=OPENROUTER_API_KEY,
    base_url="https://openrouter.ai/api/v1"
)

# ================= MODEL =================
@st.cache_resource
def load_model():
    return SentenceTransformer("all-MiniLM-L6-v2")

model = load_model()

# ================= SESSION =================
if "messages" not in st.session_state:
    st.session_state.messages = []

if "pdf_text" not in st.session_state:
    st.session_state.pdf_text = ""

if "pdf_loaded" not in st.session_state:
    st.session_state.pdf_loaded = False

# ================= TITLE =================
st.title("🤖 AI Study Assistant")
st.write("Upload PDFs → Ask Questions → Generate Notes, Quiz, Summary & Flashcards")

# ================= SIDEBAR =================
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

# ================= AUDIO =================
def speak(text):
    tts = gTTS(text)
    tts.save("speech.mp3")
    return "speech.mp3"

# ================= TFIDF =================
def get_tfidf_answer(text, question):
    sentences = re.split(r"(?<=[.!?]) +", text)

    vectorizer = TfidfVectorizer(stop_words="english")
    X = vectorizer.fit_transform(sentences + [question])

    similarity = cosine_similarity(X[-1], X[:-1])[0]

    top = similarity.argsort()[-3:][::-1]

    return " ".join([sentences[i] for i in top])

# ================= FAISS =================
def create_faiss_index(text):
    sentences = re.split(r"(?<=[.!?]) +", text)

    embeddings = model.encode(sentences)

    index = faiss.IndexFlatL2(embeddings.shape[1])

    index.add(np.array(embeddings))

    return index, sentences

def get_faiss_answer(question):
    q_vec = model.encode([question])

    D, I = st.session_state.index.search(
        np.array(q_vec),
        k=3
    )

    return " ".join(
        [st.session_state.sentences[i] for i in I[0]]
    )

# ================= OPENROUTER =================
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

# ================= LOAD PDF =================
if pdfs:

    text = ""

    for pdf in pdfs:

        reader = PdfReader(pdf)

        for page in reader.pages:

            content = page.extract_text()

            if content:
                text += content

    text = re.sub(r"\s+", " ", text)

    if text.strip():

        st.session_state.pdf_text = text

        st.session_state.index, st.session_state.sentences = create_faiss_index(text)

        st.session_state.pdf_loaded = True

        st.success("✅ PDF Loaded Successfully")

# ================= SEARCH MODE =================
mode = st.selectbox(
    "Search Mode",
    ["TF-IDF", "FAISS", "Hybrid"]
)

# ================= CHAT =================
st.markdown("---")
st.subheader("💬 Chat with PDF")

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])

question = st.chat_input("Ask from your PDFs")

if question:

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

# ================= NOTES =================
st.markdown("---")
st.subheader("🧾 AI Notes")

if st.button("Generate Notes"):

    if st.session_state.pdf_loaded:

        notes = ask_ai(
            f"Generate study notes:\n{st.session_state.pdf_text[:4000]}"
        )

        st.write(notes)

# ================= QUIZ =================
st.markdown("---")
st.subheader("📝 AI Quiz")

difficulty = st.selectbox(
    "Difficulty",
    ["Easy", "Medium", "Hard"]
)

if st.button("Generate Quiz"):

    if st.session_state.pdf_loaded:

        quiz = ask_ai(
            f"Generate a {difficulty} MCQ quiz:\n{st.session_state.pdf_text[:4000]}"
        )

        st.write(quiz)

# ================= FLASHCARDS =================
st.markdown("---")
st.subheader("📚 Flashcards")

if st.button("Generate Flashcards"):

    if st.session_state.pdf_loaded:

        flashcards = ask_ai(
            f"Create flashcards:\n{st.session_state.pdf_text[:4000]}"
        )

        st.write(flashcards)

# ================= SUMMARY =================
st.markdown("---")
st.subheader("📄 Summary")

if st.button("Generate Summary"):

    if st.session_state.pdf_loaded:

        summary = ask_ai(
            f"Summarize:\n{st.session_state.pdf_text[:4000]}"
        )

        st.write(summary)

# ================= YOUTUBE =================
st.markdown("---")
st.subheader("🎥 Learn From YouTube")

topic = st.text_input("Enter topic")

def search_youtube(query):

    url = "https://www.googleapis.com/youtube/v3/search"

    params = {
        "part": "snippet",
        "q": query,
        "type": "video",
        "maxResults": 3,
        "key": YOUTUBE_API_KEY
    }

    response = requests.get(url, params=params)

    if response.status_code != 200:
        return []

    data = response.json()

    videos = []

    for item in data.get("items", []):

        vid = item["id"]["videoId"]

        videos.append(
            f"https://www.youtube.com/watch?v={vid}"
        )

    return videos

if st.button("Search Videos"):

    videos = search_youtube(topic)

    for v in videos:
        st.video(v)

# ================= FOOTER =================
st.markdown("---")
st.caption("🚀 Built with Streamlit + OpenRouter + FAISS")