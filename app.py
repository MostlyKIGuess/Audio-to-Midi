import streamlit as st
import os
import logging
import tempfile
import traceback
import tensorflow as tf
from basic_pitch.inference import predict_and_save
from basic_pitch import ICASSP_2022_MODEL_PATH
from audio_recorder_streamlit import audio_recorder
import sys
import subprocess

logging.basicConfig(level=logging.ERROR)
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
tf.get_logger().setLevel('ERROR')

def ensure_model_dependencies():
    try:
        import tensorflow
    except ImportError:
        st.warning("Installing missing TensorFlow dependencies...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "basic-pitch[tf]"])
        st.success("Dependencies installed. Please restart the app.")
        st.stop()
        
ensure_model_dependencies()

st.set_page_config(layout="wide", page_title="Audio to MIDI Converter")

def process_audio(audio_file_path, output_directory, source_filename="input_audio"):
    """Processes an audio file and save the MIDI output."""
    try:
        model_path_to_load = ICASSP_2022_MODEL_PATH
        
        with st.status("Converting audio to MIDI...") as status:
            if not os.path.exists(model_path_to_load):
                st.error(f"Model path not found at {model_path_to_load}")
                return None, None

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

        base_name = os.path.splitext(os.path.basename(source_filename))[0]
        midi_file_path = os.path.join(output_directory, f"{base_name}_basic_pitch.mid")

        if os.path.exists(midi_file_path):
            return midi_file_path, base_name
        else:
            st.error("MIDI file generation failed.")
            return None, None

    except Exception as e:
        print(f"Error during transcription: {e}")
        print(traceback.format_exc())
        st.error(f"Transcription error: {type(e).__name__}")
        return None, None

st.title("Audio to MIDI Converter")
st.write("Upload an audio file or record audio directly in the browser.")

#  debuggin for model path
logging.info(f"Model path: {ICASSP_2022_MODEL_PATH}")
if not os.path.exists(ICASSP_2022_MODEL_PATH):
    st.error("Basic Pitch model path not found.")
    st.stop()

tab1, tab2 = st.tabs(["Upload File", "Record Audio"])

with tab1:
    st.header("Upload an Audio File")
    uploaded_file = st.file_uploader(
        "Choose an audio file (.wav, .mp3, .ogg, .flac)",
        type=['wav', 'mp3', 'ogg', 'flac'],
        key="file_uploader"
    )

    if uploaded_file:
        st.audio(uploaded_file.getvalue())

        if st.button("Convert Uploaded Audio to MIDI", key="convert_upload"):
            file_extension = uploaded_file.name.split('.')[-1].lower()
            with tempfile.TemporaryDirectory() as temp_dir:
                # original filename ( can we get attacked here? i hope not)
                temp_audio_path = os.path.join(temp_dir, uploaded_file.name)
                output_dir = os.path.join(temp_dir, "midi_output_upload")
                os.makedirs(output_dir, exist_ok=True)

                try:
                    with open(temp_audio_path, "wb") as f:
                        f.write(uploaded_file.getvalue())

                    if os.path.exists(temp_audio_path) and os.path.getsize(temp_audio_path) > 0:
                        st.success(f"Audio saved ({os.path.getsize(temp_audio_path)} bytes)")

                        with st.spinner("Processing uploaded audio..."):
                            midi_file_path, base_name = process_audio(temp_audio_path, output_dir, uploaded_file.name)

                        if midi_file_path and os.path.exists(midi_file_path):
                            st.success("MIDI conversion successful!")

                            with open(midi_file_path, "rb") as f:
                                midi_bytes = f.read()

                            st.download_button(
                                label="Download MIDI File",
                                data=midi_bytes,
                                file_name=f"{base_name}_basic_pitch.mid",
                                mime="audio/midi",
                                key="download_upload"
                            )
                        elif not midi_file_path:
                             st.warning("Conversion process did not return a MIDI file path.")
                        else:
                             st.error("MIDI file was not found after processing.")
                    else:
                        st.error("Failed to save uploaded audio file. Please try again.")

                except Exception as e:
                    st.error(f"Error processing uploaded audio: {type(e).__name__}")
                    print(traceback.format_exc())
    else:
        st.info("Upload an audio file to begin.")


with tab2:
    st.header("Record Audio from Microphone")
    st.write("Click the microphone icon to start recording. Click again to stop.")
    st.write("Note:Yellow -> recording, green-> ready to record")

    audio_bytes = audio_recorder(
        text="Click to Record:",
        recording_color="#e8b62c",
        neutral_color="#6aa36f",
        icon_name="microphone",
        icon_size="3x",
        pause_threshold=8.0, # pause after 8 seconds of silence , helps if someone leaves it open
        # sample_rate=41_000 #41k is default
    )

    if audio_bytes:
        st.subheader("Recorded Audio")
        st.audio(audio_bytes, format="audio/wav")

        if st.button("Convert Recorded Audio to MIDI", key="convert_record"):
            with tempfile.TemporaryDirectory() as temp_dir:
                temp_audio_path = os.path.join(temp_dir, "recorded_audio.wav")
                output_dir = os.path.join(temp_dir, "midi_output_record")
                os.makedirs(output_dir, exist_ok=True)

                try:
                    with open(temp_audio_path, "wb") as f:
                        f.write(audio_bytes)

                    if os.path.exists(temp_audio_path) and os.path.getsize(temp_audio_path) > 0:
                        st.success(f"Recorded audio saved ({os.path.getsize(temp_audio_path)} bytes)")

                        with st.spinner("Processing recorded audio..."):
                            midi_file_path, base_name = process_audio(temp_audio_path, output_dir, "recorded_audio.wav")

                        if midi_file_path and os.path.exists(midi_file_path):
                            st.success("MIDI conversion successful!")

                            with open(midi_file_path, "rb") as f:
                                midi_bytes = f.read()

                            st.download_button(
                                label="Download MIDI File",
                                data=midi_bytes,
                                file_name=f"{base_name}_basic_pitch.mid",
                                mime="audio/midi",
                                key="download_record"
                            )
                        elif not midi_file_path:
                            st.warning("Conversion process did not return a MIDI file path.")
                        else:
                            st.error("MIDI file was not found after processing.")
                    else:
                        st.error("Failed to save recorded audio file. Please try again.")

                except Exception as e:
                    st.error(f"Error processing recorded audio: {type(e).__name__}")
                    print(traceback.format_exc())
    else:
        st.info("Click the microphone icon above to start recording.")
