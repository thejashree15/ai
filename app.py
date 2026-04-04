import streamlit as st
from PyPDF2 import PdfReader
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import re
import time

st.set_page_config(page_title="AI Study Assistant", page_icon="🤖", layout="wide")

# 🔥 CUSTOM CSS (PREMIUM LOOK)
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
    st.markdown("### 🚀 About")
    st.write("💡 AI Study Assistant")
    st.write("📚 Ask questions from PDFs")
    st.write("⚡ Built with Streamlit")

# 🔥 TITLE
st.markdown("<h1>🤖 AI Study Assistant</h1>", unsafe_allow_html=True)
st.caption("✨ Premium AI PDF Chat Experience")

# 🔥 SESSION STATE
if "messages" not in st.session_state:
    st.session_state.messages = []

if "pdf_text" not in st.session_state:
    st.session_state.pdf_text = ""

# 🔥 LOAD MULTIPLE PDFs
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

    # Show user message
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

    # 🔥 SAVE ANSWER
    st.session_state.messages.append({"role": "assistant", "content": f"🤖 {answer}"})

    # 🔥 TYPING ANIMATION
    with st.chat_message("assistant"):
        placeholder = st.empty()
        typed_text = ""

        for word in answer.split():
            typed_text += word + " "
            placeholder.markdown(f"🤖 {typed_text}")
            time.sleep(0.03)