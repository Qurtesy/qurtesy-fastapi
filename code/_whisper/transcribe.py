import io
import whisper
from pydub import AudioSegment
from datetime import datetime

# Load Whisper model
MODEL_NAME = "medium.en"  # Options: "base.en", "medium.en", "turbo", etc.
print(f"🔄 Initializing model: {MODEL_NAME}")
model: whisper.model.Whisper = whisper.load_model(MODEL_NAME)
print(f"✅ Initialized successfully")


def transcribe_audio_blob(blob_data, filename):
    """
    Transcribes audio from a blob using Whisper.

    Args:
        blob_data: The audio data as a blob (bytes).
        filename: The original filename of the audio (e.g., "audio.mp3").

    Returns:
        The transcribed text, or None if an error occurs.
    """
    # try:

    # Convert blob_data to an AudioSegment object
    audio = AudioSegment.from_file(io.BytesIO(blob_data), format=filename.split(".")[-1])
    
    # Export audio as WAV format (Whisper requires WAV for optimal performance)
    buffer = io.BytesIO()
    audio.export(buffer, format="wav")
    buffer.seek(0)  # Move to the beginning of the buffer

    import torchaudio
    buffer, _ = torchaudio.load(buffer)
    
    # Start transcription
    start_time = datetime.now()
    buffer = whisper.pad_or_trim(buffer)
    # transcript = model.transcribe(buffer)  # Pass buffer instead of NumPy array
    mel = whisper.log_mel_spectrogram(buffer, n_mels=model.dims.n_mels).to(model.device)
    options = whisper.DecodingOptions(language='en')
    transcript = whisper.decode(model, mel, options)
    end_time = datetime.now()
    
    print(f"⏳ Transcription time: {end_time - start_time}")
    return transcript[0].text

    # except Exception as e:
    #     print(f"❌ Error transcribing audio: {e}")
    #     return None
