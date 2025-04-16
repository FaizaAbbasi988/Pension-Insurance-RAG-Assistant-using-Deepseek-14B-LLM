import streamlit as st
import pyaudio
import wave
import io
import requests
import os
from datetime import datetime
import threading

# Configuration
API_URL = "http://localhost:8000/algorithm/api/insurance/transcribe"
AUDIO_DIR = "recordings"
os.makedirs(AUDIO_DIR, exist_ok=True)

# Audio settings
SAMPLE_RATE = 16000
CHUNK_SIZE = 1024
FORMAT = pyaudio.paInt16
CHANNELS = 1

# Classification options
CLASSIFICATION_OPTIONS = {
    "policy Advice": "政策咨询",
    "Business consulting": "业务咨询",
    "Procedures": "办理流程",
    "Platform operations": "平台操作",
    "Phone numbers": "办理电话"
}

# Initialize PyAudio
p = pyaudio.PyAudio()

def record_audio(stop_flag, audio_frames):
    """Record audio from microphone"""
    stream = p.open(
        format=FORMAT,
        channels=CHANNELS,
        rate=SAMPLE_RATE,
        input=True,
        frames_per_buffer=CHUNK_SIZE
    )

    while not stop_flag.is_set():
        data = stream.read(CHUNK_SIZE, exception_on_overflow=False)
        audio_frames.append(data)

    stream.stop_stream()
    stream.close()

def save_audio(audio_frames):
    """Save recorded audio to file"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{AUDIO_DIR}/recording_{timestamp}.wav"

    with wave.open(filename, 'wb') as wf:
        wf.setnchannels(CHANNELS)
        wf.setsampwidth(p.get_sample_size(FORMAT))
        wf.setframerate(SAMPLE_RATE)
        wf.writeframes(b''.join(audio_frames))

    return filename

def transcribe_audio(audio_data, classification="general"):
    try:
        audio_file = io.BytesIO()
        with wave.open(audio_file, 'wb') as wf:
            wf.setnchannels(CHANNELS)
            wf.setsampwidth(p.get_sample_size(FORMAT))
            wf.setframerate(SAMPLE_RATE)
            wf.writeframes(audio_data)

        audio_file.seek(0)
        files = {'file': ('audio.wav', audio_file, 'audio/wav')}
        data = {'classification': classification}
        # Important: Use data parameter for form data
        response = requests.post(API_URL, files=files, data=data)
        return handle_response(response)
    except Exception as e:
        return {'error': f"Transcription error: {str(e)}"}

def send_text_question(text, classification="general"):
    try:
        files = {'file': ('question.txt', io.StringIO(text), 'text/plain')}
        data = {'classification': classification}
        # Important: Use data parameter for form data
        response = requests.post(API_URL, files=files, data=data)
        return handle_response(response)
    except Exception as e:
        return {'error': f"API error: {str(e)}"}

def handle_response(response):
    """Handle API response"""
    if response.status_code == 200:
        return {
            'question': response.json().get('question', ''),
            'answer': response.json().get('answer', ''),
            'classification': response.json().get('classification', 'general')
        }
    else:
        return {'error': response.text}

def main():
    # Custom CSS for crisp display
    st.markdown("""
        <style>
            .question-box {
                background-color: #f8f9fa;
                border-radius: 8px;
                padding: 15px;
                margin-bottom: 15px;
                border-left: 4px solid #6c757d;
                font-size: 15px;
                line-height: 1.6;
            }
            .answer-box {
                background-color: #e7f5ff;
                border-radius: 8px;
                padding: 15px;
                margin-bottom: 20px;
                border-left: 4px solid #228be6;
                font-size: 15px;
                line-height: 1.6;
            }
            .recording-title {
                color: #495057;
                margin-bottom: 10px;
            }
            .audio-file {
                font-size: 12px;
                color: #868e96;
                margin-top: 5px;
            }
            .tab-content {
                padding: 15px 0;
            }
            .classification-tag {
                display: inline-block;
                padding: 2px 8px;
                border-radius: 12px;
                background-color: #e6f7ff;
                color: #1890ff;
                font-size: 12px;
                margin-left: 8px;
            }
        </style>
    """, unsafe_allow_html=True)

    # Initialize session state
    if 'recording' not in st.session_state:
        st.session_state.recording = False
    if 'transcriptions' not in st.session_state:
        st.session_state.transcriptions = []
    if 'text_question' not in st.session_state:
        st.session_state.text_question = ""
    if 'classification' not in st.session_state:
        st.session_state.classification = "general"

    st.title("🗣️ 语音问答助理")
    st.markdown("记录你的问题并实时得到人工智能的答案")

    # Classification selector (shared between both tabs)
    st.session_state.classification = st.selectbox(
        "问题分类:",
        options=list(CLASSIFICATION_OPTIONS.keys()),
        format_func=lambda x: CLASSIFICATION_OPTIONS[x],
        index=0
    )

    # Create tabs for different input methods
    tab1, tab2 = st.tabs(["🎤 语音输入", "✏️ 文字输入"])

    with tab1:
        # UI layout for audio recording
        col1, col2 = st.columns(2)

        # Create a stop flag and audio frame list
        if 'stop_flag' not in st.session_state:
            st.session_state.stop_flag = threading.Event()
        if 'audio_frames' not in st.session_state:
            st.session_state.audio_frames = []

        # Start recording
        with col1:
            if st.button("🎤 开始录制", disabled=st.session_state.recording,
                        help="点击开始记录你的问题"):
                st.session_state.recording = True
                st.session_state.stop_flag.clear()
                st.session_state.audio_frames = []
                threading.Thread(
                    target=record_audio,
                    args=(st.session_state.stop_flag, st.session_state.audio_frames)
                ).start()
                st.rerun()

        # Stop recording
        with col2:
            if st.button("⏹️ 停止录音", disabled=not st.session_state.recording,
                        help="讲完后点击"):
                st.session_state.recording = False
                st.session_state.stop_flag.set()
                st.rerun()

        # Recording status
        if st.session_state.recording:
            st.warning("🔴 正在录音... 现在说出你的问题")
        else:
            st.info("🟢 准备录制-按开始录制")

        # Process transcription after stopping
        if not st.session_state.recording and st.session_state.audio_frames:
            with st.spinner("🔍 处理您的问题并生成答案..."):
                audio_data = b''.join(st.session_state.audio_frames)
                filename = save_audio(st.session_state.audio_frames)
                result = transcribe_audio(audio_data, st.session_state.classification)

                if 'error' in result:
                    st.error(f"Error: {result['error']}")
                else:
                    st.session_state.transcriptions.append({
                        'filename': filename,
                        'question': result['question'],
                        'answer': result['answer'],
                        'type': 'audio',
                        'classification': result.get('classification', 'general')
                    })

                # Clear audio frames after processing
                st.session_state.audio_frames = []

    with tab2:
        # Text input section
        st.session_state.text_question = st.text_area(
            "输入你的问题:",
            value=st.session_state.text_question,
            height=100,
            placeholder="在这里输入你的问题..."
        )

        if st.button("📤 提交问题", help="点击提交文字问题"):
            if st.session_state.text_question.strip():
                with st.spinner("🔍 处理您的问题并生成答案..."):
                    result = send_text_question(
                        st.session_state.text_question,
                        st.session_state.classification
                    )
                    
                    if 'error' in result:
                        st.error(f"Error: {result['error']}")
                    else:
                        st.session_state.transcriptions.append({
                            'filename': None,
                            'question': result['question'],
                            'answer': result['answer'],
                            'type': 'text',
                            'classification': result.get('classification', 'general')
                        })
                        st.session_state.text_question = ""  # Clear the input
            else:
                st.warning("请输入有效的问题")

    # Display transcription history
    if st.session_state.transcriptions:
        st.markdown("## 📚 问答历史")
        st.markdown("---")

    for i, item in enumerate(reversed(st.session_state.transcriptions)):
        source_type = "🎙️ 录音" if item['type'] == 'audio' else "✏️ 文字输入"
        classification_label = CLASSIFICATION_OPTIONS.get(item.get('classification', 'general'), '一般咨询')
        
        st.markdown(
            f'<div class="recording-title">'
            f'{source_type} {len(st.session_state.transcriptions)-i} '
            f'<span class="classification-tag">{classification_label}</span>'
            f'</div>', 
            unsafe_allow_html=True
        )
        
        st.markdown("**您的问题:**")
        st.markdown(f'<div class="question-box">{item["question"]}</div>', 
                   unsafe_allow_html=True)
        
        st.markdown("**AI 回答:**")
        st.markdown(f'<div class="answer-box">{item["answer"]}</div>', 
                   unsafe_allow_html=True)
        
        if item['type'] == 'audio' and item['filename']:
            st.markdown(f'<div class="audio-file">音频文件: {item["filename"]}</div>', 
                       unsafe_allow_html=True)
        st.markdown("---")

    if st.session_state.transcriptions:
        if st.button("🧹 清除所有记录", help="清除所有问答历史"):
            st.session_state.transcriptions = []
            st.rerun()

if __name__ == "__main__":
    main()