# AI Interview Coach Documentation

## Overview
The AI Interview Coach is a voice-enabled Streamlit application that conducts mock interviews based on your resume. It uses Google's Gemini AI to ask relevant questions and provide feedback, with speech-to-text and text-to-speech capabilities for a natural conversation experience.

## How It Works

### 1. Application Setup
```python
import streamlit as st
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
```
- **Streamlit**: Creates the web interface
- **LangChain**: Manages AI conversations and message history
- **Google Gemini**: Powers the AI interviewer

### 2. Audio Processing Functions

#### Speech-to-Text (`transcribe_audio`)
```python
def transcribe_audio(audio_bytes):
    # Converts recorded audio to text using OpenAI Whisper
```
**How it works:**
1. Takes audio bytes from the microphone recorder
2. Saves them to a temporary `.webm` file
3. Uses OpenAI Whisper (local AI model) to convert speech to text
4. Returns the transcribed text
5. Cleans up temporary files

**Requirements:**
- FFmpeg installed and in system PATH
- OpenAI Whisper: `pip install openai-whisper`

#### Text-to-Speech (`text_to_speech`)
```python
def text_to_speech(text):
    # Converts AI responses to audio using Google TTS
```
**How it works:**
1. Takes text from AI response
2. Uses Google Text-to-Speech (gTTS) to generate audio
3. Saves audio to temporary MP3 file
4. Returns file path for playback

### 3. Session State Management
```python
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "resume_text" not in st.session_state:
    st.session_state.resume_text = ""
```
**Purpose:**
- **chat_history**: Stores conversation between user and AI
- **resume_text**: Stores extracted resume content for context

### 4. Resume Upload & Processing
```python
user_resume = st.file_uploader("Upload resume", type=["pdf"])
if user_resume and st.session_state.resume_text == "":
    # Extract text from PDF and store in session
```
**Process:**
1. User uploads PDF resume
2. PyPDFLoader extracts text content
3. Text is stored in session state
4. AI sends greeting message acknowledging resume review

### 5. Audio Interface
```python
audio_input = mic_recorder(
    start_prompt="Start Recording ⏺️",
    stop_prompt="Stop Recording ⏹️", 
    just_once=False,
    key='recorder'
)
```
**Features:**
- Click to start/stop recording
- Real-time audio capture
- Automatic processing when recording stops

### 6. AI Interview Logic
```python
system_prompt = SystemMessage(content=f"""
You are an expert Interviewer. You have to take the interview of the user based on his job profile. 
Get the user's job profile from the resume context: {st.session_state.resume_text}.

Rule 1: See for the user's expertise, tools, projects and prepare the questionnaire likely.
Rule 2: Ask him to describe the project. Wait for the user's answer then ask at least 5-6 follow-up questions.
Rule 3: After 5-6 technical follow-ups, switch to HR questions.
""")
```

**Interview Flow:**
1. **Resume Analysis**: AI analyzes uploaded resume
2. **Technical Questions**: Asks about projects, skills, tools
3. **Deep Dive**: 5-6 follow-up questions per project
4. **HR Questions**: Behavioral and situational questions
5. **Continuous Context**: Maintains conversation history

### 7. Response Generation & Playback
```python
llm = ChatGoogleGenerativeAI(model="gemini-2.5-flash")
response = llm.invoke(full_messages)

# Display response
st.write(response.content)

# Convert to audio and play
audio_file_path = text_to_speech(response.content)
st.audio(audio_file_path, format="audio/mp3", autoplay=True)
```

## Setup Instructions

### 1. Install Dependencies
```bash
pip install streamlit langchain-google-genai langchain-community
pip install streamlit-mic-recorder gtts speech-recognition
pip install openai-whisper PyPDF2 python-dotenv
```

### 2. Install FFmpeg
**Windows:**
1. Download from: https://www.gyan.dev/ffmpeg/builds/
2. Extract to `C:\ffmpeg`
3. Add `C:\ffmpeg\bin` to system PATH
4. Restart terminal

**Verify installation:**
```bash
ffmpeg -version
```

### 3. Setup Environment Variables
Create `.env` file:
```
GOOGLE_API_KEY=your_google_api_key_here
```

### 4. Run Application
```bash
streamlit run app.py
```

## Usage Guide

### Step 1: Upload Resume
- Click "Browse files" and select your PDF resume
- Wait for "I've studied your resume" message

### Step 2: Start Interview
- Click "Start Recording ⏺️" to begin speaking
- Answer the AI's questions naturally
- Click "Stop Recording ⏹️" when done

### Step 3: Continue Conversation
- AI will ask follow-up questions based on your resume
- Technical questions about projects and skills
- HR questions about experience and goals

## Technical Architecture

```
User Input (Audio) → Whisper (Speech-to-Text) → Gemini AI → Response Generation → gTTS (Text-to-Speech) → Audio Output
                                                     ↓
                                              Resume Context + Chat History
```

## Key Features

1. **Voice-First Interface**: Natural conversation experience
2. **Resume-Aware**: Questions tailored to your background
3. **Contextual Follow-ups**: Deep dive into specific topics
4. **Real-time Processing**: Immediate responses
5. **Audio Feedback**: Spoken responses for immersive experience

## Troubleshooting

### Common Issues:

**"FFmpeg not found"**
- Install FFmpeg and add to PATH
- Restart terminal and Streamlit app

**"Audio processing error"**
- Check microphone permissions
- Ensure FFmpeg is properly installed

**"API quota exceeded"**
- Check Google API key and billing
- Verify GOOGLE_API_KEY in .env file

**No audio playback**
- Check browser audio permissions
- Ensure speakers/headphones are connected

## File Structure
```
AI_Interview_Coach/
├── app.py              # Main application
├── .env               # Environment variables
└── requirements.txt   # Dependencies
```

This documentation covers all aspects of the AI Interview Coach, from technical implementation to user guidance, making it accessible for both developers and end-users.