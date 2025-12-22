import streamlit as st
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
import tempfile
from langchain_community.document_loaders import PyPDFLoader
import os
from dotenv import load_dotenv
from streamlit_mic_recorder import mic_recorder
from gtts import gTTS
load_dotenv()


os.environ["GOOGLE_API_KEY"] = os.getenv("GOOGLE_API_KEY")

# --- Helper Functions ---

def transcribe_audio(audio_bytes):
    """Converts audio to text using OpenAI Whisper (Local)"""
    if not audio_bytes:
        return None
    
    try:
        import whisper
        import subprocess
        
        # Check if ffmpeg is available
        subprocess.run(["ffmpeg", "-version"], capture_output=True, check=True)
        
        # Save audio bytes to temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix=".webm") as temp_file:
            temp_file.write(audio_bytes)
            temp_path = temp_file.name
        
        # Load Whisper model and transcribe
        model = whisper.load_model("tiny")
        result = model.transcribe(temp_path, fp16=False)
        
        # Cleanup
        os.remove(temp_path)
        return result["text"]
        
    except subprocess.CalledProcessError:
        return "FFmpeg not found. Please restart your terminal after installing FFmpeg."
    except Exception as e:
        return f"Audio error: {str(e)}"

def text_to_speech(text):
    """Converts text to audio using gTTS (Free)"""
    tts = gTTS(text=text, lang='en')
    with tempfile.NamedTemporaryFile(delete=False, suffix=".mp3") as tmp_audio:
        tts.save(tmp_audio.name)
        return tmp_audio.name

# --- Session State Setup ---
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "resume_text" not in st.session_state:
    st.session_state.resume_text = ""

st.title("🎤 Free AI Voice Interview Coach")

# --- 1. Resume Extraction ---
user_resume = st.file_uploader("Upload resume", type=["pdf"])
if user_resume and st.session_state.resume_text == "":
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
        tmp_file.write(user_resume.getvalue())
        tmp_path = tmp_file.name

    loader = PyPDFLoader(tmp_path)
    docs = loader.load()
    st.session_state.resume_text = "\n".join([doc.page_content for doc in docs])
    
    greeting = "I've studied your resume. Which project should we discuss first?"
    st.session_state.chat_history.append(AIMessage(content=greeting))
    os.remove(tmp_path)

# --- 2. Display Chat History ---
for message in st.session_state.chat_history:
    if isinstance(message, AIMessage):
        with st.chat_message("assistant"):
            st.write(message.content)
    elif isinstance(message, HumanMessage):
        with st.chat_message("user"):
            st.write(message.content)

# --- 3. Audio Input Interface ---
st.write("### Answer the Question:")
audio_input = mic_recorder(
    start_prompt="Start Recording ⏺️",
    stop_prompt="Stop Recording ⏹️", 
    just_once=False,
    key='recorder'
)

# Logic to handle Audio Input
if audio_input and 'bytes' in audio_input:
    # Rate limiting check
    if 'last_request_time' not in st.session_state:
        st.session_state.last_request_time = 0
    
    import time
    current_time = time.time()
    if current_time - st.session_state.last_request_time < 3:  # 3 second cooldown
        st.warning("Please wait 3 seconds between requests to avoid rate limits.")
    else:
        # A. Transcribe User Audio
        user_text = transcribe_audio(audio_input['bytes'])
        
        if user_text and not user_text.startswith("Audio"):
            st.session_state.chat_history.append(HumanMessage(content=user_text))
            with st.chat_message("user"):
                st.write(user_text)
            
            st.session_state.last_request_time = current_time

        # B. AI Logic with rate limiting
        try:
            system_prompt = SystemMessage(content=f"""
            You are an expert Interviewer. You have to take the interview of the user based on his job profile. Get the user's job profile from the resume context: {st.session_state.resume_text}.

            Rule 1: See for the user's expertise, tools, projects and prepare the questionnaire likely.
            Rule 2: Ask him to describe the project. Wait for the user's answer then ask at least 5-6 follow-up questions waiting for user's answer after each to confirm his understanding on the project.
            Rule 3: After 5-6 technical follow-ups, switch to HR questions.
            """)
            
            full_messages = [system_prompt] + st.session_state.chat_history

            llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash", temperature=0.7)
            
            # Add retry logic for rate limits
            max_retries = 3
            for attempt in range(max_retries):
                try:
                    response = llm.invoke(full_messages)
                    break
                except Exception as e:
                    if "rate limit" in str(e).lower() and attempt < max_retries - 1:
                        st.warning(f"Rate limit hit, retrying in {2**attempt} seconds...")
                        time.sleep(2**attempt)  # Exponential backoff
                    else:
                        raise e
            
            st.session_state.chat_history.append(AIMessage(content=response.content))
            with st.chat_message("assistant"):
                st.write(response.content)

            # C. Output Audio (Free gTTS) - Optional
            # audio_file_path = text_to_speech(response.content)
            # st.audio(audio_file_path, format="audio/mp3", start_time=0, autoplay=True)
            
        except Exception as e:
            st.error(f"AI processing error: {str(e)}")
            st.info("Please try again in a few moments.")
