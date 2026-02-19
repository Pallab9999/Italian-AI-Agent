import os
import warnings
import numpy as np
import sounddevice as sd
from scipy.io.wavfile import write
from dotenv import load_dotenv
from elevenlabs.client import ElevenLabs
from deep_translator import GoogleTranslator

# Suppress the harmless Pydantic warning
warnings.filterwarnings("ignore", category=UserWarning, module='elevenlabs')

# 1. Load API Key
load_dotenv()
client = ElevenLabs(api_key=os.getenv("ELEVENLABS_API_KEY"))

# 2. Windows Microphone Settings
RATE = 44100
WAVE_OUTPUT_FILENAME = "temp_italian.wav"
TRANSCRIPT_FILENAME = "Meeting_Transcript.txt"

CHUNK_DURATION = 0.5
CHUNK_SAMPLES = int(RATE * CHUNK_DURATION)
SILENCE_LIMIT = 4.0
SILENCE_CHUNKS = int(SILENCE_LIMIT / CHUNK_DURATION)
VOLUME_THRESHOLD = 500

full_conversation = []

print("🤖 AI Agent is now actively listening... (Press Ctrl+C to stop)")

try:
    while True:
        audio_buffer = []
        silent_chunk_count = 0
        has_spoken = False
        
        with sd.InputStream(samplerate=RATE, channels=1, dtype='int16') as stream:
            print("\n🎤 Waiting for conversation to start...")
            
            while True:
                data, overflow = stream.read(CHUNK_SAMPLES)
                audio_buffer.append(data)
                volume = np.max(np.abs(data))
                
                if volume > VOLUME_THRESHOLD:
                    if not has_spoken:
                        print("🗣️ Speech detected! Listening...")
                    has_spoken = True
                    silent_chunk_count = 0
                else:
                    if has_spoken:
                        silent_chunk_count += 1
                        
                if has_spoken and silent_chunk_count >= SILENCE_CHUNKS:
                    print("⏸️ 4 seconds of silence detected. Processing voices...")
                    break 

        recording = np.concatenate(audio_buffer, axis=0)
        write(WAVE_OUTPUT_FILENAME, RATE, recording)
        
        # 3. Send to ElevenLabs
        with open(WAVE_OUTPUT_FILENAME, "rb") as audio_file:
            transcription = client.speech_to_text.convert(
                file=audio_file,
                model_id="scribe_v2",
                language_code="ita",
                diarize=True
            )
            
        # 4. Extract Speakers and Translate Individually
        if hasattr(transcription, 'words') and transcription.words:
            utterances = []
            current_speaker = None
            current_text = ""
            
            # Group the individual words by who is speaking
            for item in transcription.words:
                speaker = getattr(item, 'speaker_id', 'Unknown')
                
                # Format "speaker_1" into "Speaker 1" for cleaner reading
                if speaker and speaker.startswith("speaker_"):
                    speaker = speaker.replace("speaker_", "Speaker ")
                elif not speaker:
                    speaker = "Speaker ?"
                    
                if speaker != current_speaker:
                    if current_speaker is not None:
                        utterances.append({"speaker": current_speaker, "text": current_text.strip()})
                    current_speaker = speaker
                    current_text = item.text
                else:
                    current_text += item.text
                    
            if current_speaker is not None:
                utterances.append({"speaker": current_speaker, "text": current_text.strip()})
                
            print("\n" + "=" * 40)
            
            # Translate and print each speaker's block
            for utterance in utterances:
                it_text = utterance["text"]
                if it_text.strip():
                    en_text = GoogleTranslator(source='it', target='en').translate(it_text)
                    speaker_name = utterance["speaker"].upper()
                    
                    # Print to terminal
                    print(f"{speaker_name} 🇮🇹: {it_text}")
                    print(f"{speaker_name} 🇬🇧: {en_text}\n")
                    
                    # Save to background document
                    full_conversation.append(f"{speaker_name} 🇮🇹: {it_text}")
                    full_conversation.append(f"{speaker_name} 🇬🇧: {en_text}\n")
                    
            print("=" * 40)
        else:
            print("No recognizable speech found in that audio block.")

except KeyboardInterrupt:
    print("\n🛑 AI Agent stopped listening.")
    if full_conversation:
        print("💾 Saving the full diarized transcript...")
        with open(TRANSCRIPT_FILENAME, "w", encoding="utf-8") as file:
            file.write("=== FULL MEETING TRANSCRIPT ===\n\n")
            file.write("\n".join(full_conversation))
        print(f"✅ Saved successfully to '{TRANSCRIPT_FILENAME}'! Ciao!")