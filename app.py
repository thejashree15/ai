import streamlit as st
from PyPDF2 import PdfReader
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import re
import time
import requests

# 🔑 ADD YOUR API KEY HERE
API_KEY = "AIzaSyDsXwoXa2vm3ZzNwIs__3WAtTZfts2SoUs"

st.set_page_config(page_title="AI Study Assistant", page_icon="🤖", layout="wide")

# 🔥 CUSTOM CSS
st.markdown("""
<style>
body {
    background-color: #0E1117;
}
h1, h2, h3 {
    color: #00ADB5;
}
</style>
""", unsafe_allow_html=True)

# 🔥 SIDEBAR
with st.sidebar:
    st.markdown("## 📂 Control Panel")
    st.markdown("---")

    pdfs = st.file_uploader("📄 Upload PDFs", type="pdf", accept_multiple_files=True)

    if st.button("🧹 Clear Chat"):
        st.session_state.messages = []
        st.experimental_rerun()

    st.markdown("---")

    # 🎯 QUIZ BUTTON IN SIDEBAR
    st.markdown("### 📝 Quiz Generator")
    generate_btn = st.button("Generate Quiz")

    st.markdown("---")
    st.markdown("### 🚀 About")
    st.write("💡 AI Study Assistant")
    st.write("📚 Ask questions from PDFs")
    st.write("🎥 Learn with videos")
    st.write("⚡ Built with Streamlit")

# 🔥 TITLE
st.markdown("<h1>🤖 AI Study Assistant</h1>", unsafe_allow_html=True)
st.caption("✨ AI PDF Chat + Quiz + Video Learning")

# 🔥 SESSION STATE
if "messages" not in st.session_state:
    st.session_state.messages = []

if "pdf_text" not in st.session_state:
    st.session_state.pdf_text = ""

# 🔥 LOAD PDFs
if pdfs:
    text = ""

    for pdf in pdfs:
        reader = PdfReader(pdf)

        for page in reader.pages:
            if page.extract_text():
                text += page.extract_text()

    text = re.sub(r'\s+', ' ', text)
    text = re.sub(r'Page \d+', '', text)

    st.session_state.pdf_text = text
    st.success(f"✅ {len(pdfs)} PDF(s) uploaded successfully!")

# 🔥 DISPLAY CHAT
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# 🔥 USER INPUT
question = st.chat_input("💬 Ask anything from your PDFs...")

if question:

    st.session_state.messages.append({"role": "user", "content": f"🧑 {question}"})
    with st.chat_message("user"):
        st.markdown(f"🧑 {question}")

    if st.session_state.pdf_text == "":
        answer = "⚠️ Please upload at least one PDF."
    else:
        try:
            sentences = re.split(r'(?<=[.!?]) +', st.session_state.pdf_text)

            clean_sentences = [
                s.strip() for s in sentences
                if len(s) > 40 and not any(x in s.lower() for x in ["page", "figure"])
            ]

            vectorizer = TfidfVectorizer(stop_words='english')
            vectors = vectorizer.fit_transform(clean_sentences + [question])

            similarity = cosine_similarity(vectors[-1], vectors[:-1])[0]
            top_indices = similarity.argsort()[-5:][::-1]

            selected = [
                clean_sentences[i]
                for i in top_indices if similarity[i] > 0.2
            ]

            if selected:
                answer = " ".join(selected[:3])
                answer = " ".join(dict.fromkeys(answer.split()))
            else:
                answer = "❌ No relevant answer found."

        except:
            answer = "⚠️ Error processing your request."

    st.session_state.messages.append({"role": "assistant", "content": f"🤖 {answer}"})

    with st.chat_message("assistant"):
        placeholder = st.empty()
        typed_text = ""

        for word in answer.split():
            typed_text += word + " "
            placeholder.markdown(f"🤖 {typed_text}")
            time.sleep(0.03)

# ================= QUIZ FUNCTION ================= #

def generate_quiz(text):
    sentences = text.split(".")[:5]

    quiz = []
    for s in sentences:
        if len(s.strip()) > 20:
            quiz.append(f"What is: {s.strip()} ?")

    return quiz

# ================= SHOW QUIZ ================= #

if generate_btn:
    if st.session_state.pdf_text == "":
        st.warning("⚠️ Upload PDF first")
    else:
        st.subheader("📝 Generated Quiz")

        quiz = generate_quiz(st.session_state.pdf_text)

        for i, q in enumerate(quiz):
            st.write(f"Q{i+1}: {q}")

# ================= YOUTUBE FUNCTION ================= #

def search_youtube(query):
    url = f"https://www.googleapis.com/youtube/v3/search?part=snippet&q={query}&key={API_KEY}&maxResults=3&type=video"

    response = requests.get(url)
    data = response.json()

    videos = []

    for item in data.get("items", []):
        video_id = item["id"]["videoId"]
        title = item["snippet"]["title"]

        videos.append({
            "title": title,
            "url": f"https://www.youtube.com/watch?v={video_id}"
        })

    return videos

# ================= YOUTUBE UI ================= #

st.markdown("---")
st.subheader("🎥 Learn from Videos")

topic = st.text_input("Enter topic to learn")

if st.button("Search Videos"):
    if topic:
        videos = search_youtube(topic)

        for vid in videos:
            st.write(f"▶ {vid['title']}")
            st.video(vid['url'])