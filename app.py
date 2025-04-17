import streamlit as st
import os
import logging
import tempfile
import traceback
import tensorflow as tf
from basic_pitch.inference import predict_and_save
from basic_pitch import ICASSP_2022_MODEL_PATH

logging.basicConfig(level=logging.ERROR)
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
tf.get_logger().setLevel('ERROR')

def ensure_model_dependencies():
    import sys
    import subprocess
    try:
        import tensorflow
    except ImportError:
        st.warning("Installing missing TensorFlow dependencies...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "basic-pitch[tf]"])
        st.success("Dependencies installed. Please restart the app.")
        st.stop()
        
ensure_model_dependencies()

st.set_page_config(layout="wide", page_title="Audio to MIDI Converter")

def process_audio(audio_file_path, output_directory):
    try:
        model_path_to_load = ICASSP_2022_MODEL_PATH
        
        with st.status("Converting audio to MIDI...") as status:
            if not os.path.exists(model_path_to_load):
                st.error(f"Model path not found at {model_path_to_load}")
                return None

            status.update(label="Generating MIDI transcription...")
            predict_and_save(
                [audio_file_path],
                output_directory,
                True,    # save_midi
                False,   # sonify_midi
                False,   # save_model_outputs
                False,   # save_notes
                model_path_to_load
            )
            
        base_name = os.path.splitext(os.path.basename(audio_file_path))[0]
        midi_file_path = os.path.join(output_directory, f"{base_name}_basic_pitch.mid")
        
        if os.path.exists(midi_file_path):
            return midi_file_path
        else:
            st.error("MIDI file generation failed.")
            return None

    except Exception as e:
        print(f"Error during transcription: {e}")
        print(traceback.format_exc())
        st.error(f"Transcription error: {type(e).__name__}")
        return None

st.title("Audio to MIDI Converter")
st.write("Upload an audio file to convert it to MIDI format.")

#  debuggin for model path
logging.info(f"Model path: {ICASSP_2022_MODEL_PATH}")
if not os.path.exists(ICASSP_2022_MODEL_PATH):
    st.warning("Model path not found. Please ensure the model is correctly set up.")
    st.stop()
    
    
uploaded_file = st.file_uploader(
    "Choose an audio file (.wav, .mp3, .ogg, .flac)", 
    type=['wav', 'mp3', 'ogg', 'flac']
)

if uploaded_file:
    file_extension = uploaded_file.name.split('.')[-1].lower()
    st.audio(uploaded_file.getvalue())
    
    if st.button("Convert to MIDI"):
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_audio_path = os.path.join(temp_dir, f"input_audio.{file_extension}")
            output_dir = os.path.join(temp_dir, "midi_output")
            os.makedirs(output_dir, exist_ok=True)
            
            try:
                with open(temp_audio_path, "wb") as f:
                    f.write(uploaded_file.getvalue())
                
                if os.path.exists(temp_audio_path) and os.path.getsize(temp_audio_path) > 0:
                    st.success(f"Audio saved ({os.path.getsize(temp_audio_path)} bytes)")
                    
                    with st.spinner("Processing audio..."):
                        midi_file_path = process_audio(temp_audio_path, output_dir)
                    
                    if midi_file_path and os.path.exists(midi_file_path):
                        st.success("MIDI conversion successful!")
                        
                        with open(midi_file_path, "rb") as f:
                            midi_bytes = f.read()
                        
                        base_name = os.path.splitext(uploaded_file.name)[0]
                        
                        st.download_button(
                            label="Download MIDI File",
                            data=midi_bytes,
                            file_name=f"{base_name}_midi.mid",
                            mime="audio/midi"
                        )
                else:
                    st.error("Failed to save audio file. Please try again.")
                    
            except Exception as e:
                st.error(f"Error processing audio: {type(e).__name__}")
                print(traceback.format_exc())
else:
    st.info("Please upload an audio file to begin.")

