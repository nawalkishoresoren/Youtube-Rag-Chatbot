import streamlit as st
import requests

# --- Page Configuration ---
st.set_page_config(
    page_title="YouTube Chatbot",
    page_icon=":robot:",
    layout="centered",
)

st.title("YouTube Chatbot")

# --- Sidebar for Backend URL ---
st.sidebar.header("Backend Configuration")
backend_url = st.sidebar.text_input(
    "Backend URL", 
    value="http://127.0.0.1:8000", 
    help="Enter the URL where your FastAPI backend is running"
)

# --- Video Processing Section ---
st.header("1. Process YouTube Video")
video_url = st.text_input(
    "Enter YouTube Video URL", 
    placeholder="e.g., https://www.youtube.com/watch?v=dQw4w9WgXcQ"
)

if st.button("Process Video"):
    if video_url:
        with st.spinner("Processing video... This may take a moment."):
            try:
                response = requests.post(f"{backend_url}/process_video", json={"url": video_url})
                if response.status_code == 200:
                    st.success(response.json().get("message", "Video processed successfully!"))
                    st.session_state["video_id"] = response.json().get("video_id")
                else:
                    st.error(f"Error processing video: {response.json().get("detail", "Unknown error")}")
            except requests.exceptions.ConnectionError:
                st.error("Could not connect to the backend. Please ensure the backend is running at the specified URL.")
            except Exception as e:
                st.error(f"An unexpected error occurred: {e}")
    else:
        st.warning("Please enter a YouTube video URL.")

# --- Chat Interface Section ---
st.header("2. Ask a Question")

# Initialize chat history if not present
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat messages from history
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Chat input
if query := st.chat_input("Ask a question about the video..."):
    if "video_id" not in st.session_state:
        st.warning("Please process a video first.")
    else:
        st.session_state.messages.append({"role": "user", "content": query})
        with st.chat_message("user"):
            st.markdown(query)

        with st.chat_message("assistant"):
            with st.spinner("Getting response..."):
                try:
                    response = requests.post(
                        f"{backend_url}/ask", 
                        json={"url": video_url}, 
                        params={"query": query}
                    )
                    if response.status_code == 200:
                        answer = response.json().get("answer", "No answer found.")
                        st.markdown(answer)
                        st.session_state.messages.append({"role": "assistant", "content": answer})
                    else:
                        st.error(f"Error getting answer: {response.json().get("detail", "Unknown error")}")
                except requests.exceptions.ConnectionError:
                    st.error("Could not connect to the backend. Please ensure the backend is running.")
                except Exception as e:
                    st.error(f"An unexpected error occurred: {e}")
