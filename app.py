import fitz  # PyMuPDF for reading PDFs
from fpdf import FPDF
import base64
import streamlit as st
from summarizer import generate_summary

st.set_page_config(page_title="🧠 Text Summarizer", layout="centered")

# 💅 Load CSS file
def local_css(file_name):
    with open(file_name, encoding="utf-8") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

local_css("style.css")

st.title("📝 AI Text Summarizer")
st.caption("Built with BART model - HuggingFace 🤗")

# ⬇️ Settings for summary type and length
with st.expander("🔧 Settings"):
    summary_length = st.selectbox("Select Summary Length", ["Short", "Medium", "Long"])
    summarization_type = st.radio("Choose Summarization Type", ["Abstractive"])

length_config = {
    "Short": (30, 60),
    "Medium": (60, 130),
    "Long": (130, 250)
}
min_len, max_len = length_config[summary_length]

# ⬇️ Text input or file upload
st.markdown("### 📄 Enter text or upload a file:")
uploaded_file = st.file_uploader("Upload .txt or .pdf file", type=["txt", "pdf"])
text_input = ""

if uploaded_file is not None:
    if uploaded_file.type == "text/plain":
        text_input = uploaded_file.read().decode("utf-8")
    elif uploaded_file.type == "application/pdf":
        with fitz.open(stream=uploaded_file.read(), filetype="pdf") as doc:
            for page in doc:
                text_input += page.get_text()
else:
    text_input = st.text_area("Or paste your text below:", height=250)

# ⬇️ Function to create downloadable PDF
def create_pdf(summary_text):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.multi_cell(0, 10, summary_text)
    pdf_output = "summary.pdf"
    pdf.output(pdf_output)
    return pdf_output

summary = ""

if st.button("✨ Generate Summary"):
    if not text_input.strip():
        st.warning("Please paste or upload some content.")
    else:
        with st.spinner("Generating summary..."):
            try:
                summary = generate_summary(text_input, max_len=max_len, min_len=min_len)
                st.success("✅ Summary generated!")
                st.markdown("### 🧾 Summary:")
                st.text_area("Summary Output", summary, height=200)

                st.download_button("📥 Download as .txt", summary, file_name="summary.txt")

                pdf_file_path = create_pdf(summary)
                with open(pdf_file_path, "rb") as f:
                    pdf_data = f.read()
                    st.download_button(
                        label="📄 Download as PDF",
                        data=pdf_data,
                        file_name="summary.pdf",
                        mime="application/pdf"
                    )
            except Exception as e:
                st.error(f"❌ Error: {e}")
