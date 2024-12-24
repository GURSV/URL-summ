import streamlit as st
import requests
from bs4 import BeautifulSoup
from transformers import pipeline, AutoModelForSeq2SeqLM, AutoTokenizer
from rich.console import Console
from rich.text import Text
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os

st.markdown("""
    <style>
        @import url('https://cdn.jsdelivr.net/npm/@fontsource/iosevka/400.css');
            

        /* Custom styling for the text area */
        .stTextArea textarea {
            font-family: 'Iosevka', 'Georgia', serif;
            font-size: 16px;
            line-height: 1.6;
        }
        
        .footer {
            position: fixed;
            bottom: 0;
            left: 0;
            right: 0;
            background-color:rgb(0, 0, 0);
            text-align: center;
            padding: 10px;
            font-size: 14px;
            color: white;
        }
        .footer a {
            color: inherit;
            text-decoration: underline;
        }
        .footer a:hover {
            color:rgb(57, 115, 190);
        }
    </style>
""", unsafe_allow_html=True)

col1, col2, col3 = st.columns(3)

with col1:
    st.image("scene.jpg", caption="", width=2000)

st.title("_URL Summarizer_")
st.markdown(":gray[This application summarizes a URL's content into structured format] 🗿")

st.html("<br/>")

url = st.text_input("Enter URL", value="", placeholder="https://example.com")

# Actual implementation...
def extract_text_from_url(url):
    try:
        response = requests.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, "html.parser")

        paragraphs = soup.find_all("p")
        text = " ".join([para.get_text() for para in paragraphs])
        return text.strip()
    except Exception as e:
        st.error(f"Error fetching content: {e}")
        return None

model_name = "sshleifer/distilbart-cnn-12-6"
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForSeq2SeqLM.from_pretrained(model_name)

summarizer = pipeline("summarization", model=model, tokenizer=tokenizer, framework="pt")

def split_into_chunks(text, max_tokens=1024):
    """Split text into chunks of a specified max token length."""
    words = text.split()
    chunks = []
    current_chunk = []
    current_length = 0

    for word in words:
        current_chunk.append(word)
        current_length += len(word) + 1
        if current_length >= max_tokens:
            chunks.append(" ".join(current_chunk))
            current_chunk = []
            current_length = 0

    if current_chunk:
        chunks.append(" ".join(current_chunk))

    return chunks

def summarize_large_content(content):
    """Summarize large content by splitting it into manageable chunks."""
    chunks = split_into_chunks(content, max_tokens=1024)
    full_summary = []

    for i, chunk in enumerate(chunks):
        try:
            summary = summarizer(chunk, max_length=200, min_length=50, do_sample=False)
            full_summary.append(summary[0]["summary_text"])
        except Exception as e:
            st.error(f"Error summarizing chunk {i + 1}: {e}")

    return " ".join(full_summary)

def format_summary(summary):
    points = summary.split(". ")
    formatted_summary = ""
    for point in points:
        if "for example" in point.lower():
            formatted_summary += f"{point.strip()}. \n"
        else:
            formatted_summary += f"{point.strip()}. "
    return formatted_summary.rstrip(" .") + "."

console = Console()

# For rating notification...
def send_rating_email(rating):
    sender_email = "gurmeharsinghv@gmail.com"  # Sender...
    sender_password = st.secrets["EMAIL_PASSWORD"] # Sender password...
    receiver_email = "gurmeharsinghv@gmail.com" # Receiver...
    
    message = MIMEMultipart()
    message["From"] = sender_email
    message["To"] = receiver_email
    message["Subject"] = "New Rating Received for URL Summarizer"
    
    body = f"You received a new rating of {rating} stars for your URL Summarizer application!"
    message.attach(MIMEText(body, "plain"))
    
    try:
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        
        server.login(sender_email, sender_password)
        
        text = message.as_string()
        server.sendmail(sender_email, receiver_email, text)
        server.quit()
        return True
    except Exception as e:
        st.error(f"Failed to send email notification: {str(e)}")
        return False

if st.button("Summarize"):
    if url:
        st.info("Fetching content...")
        content = extract_text_from_url(url)
        if content:
            st.info("Summarizing content...")
            raw_summary = summarize_large_content(content)
            if raw_summary:
                st.success("Summarization successful!", icon="✅")
                st.subheader("Formatted Summary")
                
                formatted_summary = format_summary(raw_summary)
                
                st.text_area(label="", value=formatted_summary, height=300)
       
                st.download_button(
                    "Download the Summary",
                    data=formatted_summary,
                    file_name="Formatted-Summary-By-GSV.txt"
                )
            else:
                st.error("Summarization failed.")
        else:
            st.error("No content found to summarize.")
    else:
        st.warning("Please enter a valid URL.")

st.html("<br/>")

st.markdown(":violet[Give your rating to this app]")
sentiment_mapping = ["one", "two", "three", "four", "five"]
selected = st.feedback("stars")
if selected is not None:
    rating = selected + 1
    
    if send_rating_email(rating):
        st.markdown("Thank you for the rating 🗿")
    else:
        st.markdown("Thank you for the rating 🗿 (Email notification failed)")

st.markdown(
    """
    <style>
        .footer {
            position: fixed;
            bottom: 0;
            left: 0;
            right: 0;
            background-color:rgb(0, 0, 0);
            text-align: center;
            padding: 10px;
            font-size: 14px;
            color: white;
        }
        .footer a {
            color: inherit;
            text-decoration: underline;
        }
        .footer a:hover {
            color:rgb(57, 115, 190);
        }
    </style>
    <div class="footer">
        Made with 🗿 by Gurmehar Singh | <a href="https://linktr.ee/GurmeharSinghV" target="_blank">My Linktree</a>
    </div>
    """,
    unsafe_allow_html=True
)