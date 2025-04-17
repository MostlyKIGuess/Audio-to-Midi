# Audio to MIDI Converter

A simple Streamlit app to convert audio files or microphone recordings to MIDI using Spotify's Basic Pitch.

## Features
- Upload audio files (WAV, MP3, OGG, FLAC) and convert to MIDI
- Record audio in the browser and convert to MIDI
- Download the generated MIDI file



 Deployed Version Available at [https://audio-to-midi.streamlit.app](https://audio-to-midi.streamlit.app)

# Running Locally

## Using Docker

1. You can build the image by yourself or pull it from dockerhub.

Building:
```bash
docker build -t audio-to-midi-converter .
```
Pulling:
```bash
docker pull mostlyk/audio-to-midi
```
2. Run the container:
```bash
docker run -p 8501:8501 mostlyk/audio-to-midi
```
3. Open your browser and go to `http://localhost:8501` to access the app.

## Using Conda

1. Create a new conda environment:
```bash
conda env create -f environment.yml
```
2. Activate the environment:
```bash
conda activate audio-to-midi
```
3. Run the Streamlit app:
```bash
streamlit run app.py
```
4. Open your browser and go to `http://localhost:8501` to access the app.
