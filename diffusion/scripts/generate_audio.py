from pydub import AudioSegment
import json
import io
import soundfile as sf
import os
from kokoro.pipeline import KPipeline

def generate_audio(script_data):
    pipeline = KPipeline(lang_code='en')
        
    all_audio = []
    for segment in script_data["audio_script"]:
        speaker_id = "am_adam" if segment["speaker"] in ["default", "narrator_male"] else "af_heart"
        audio = pipeline(text=segment["text"], voice=speaker_id, speed=segment["speed"])
        
        # Collect audio chunks
        buffer = io.BytesIO()
        for _, _, chunk in audio:
            sf.write(buffer, chunk, 24000, format='WAV')
        buffer.seek(0)
        all_audio.append(buffer.read())
    
    return all_audio

def merge_audio(audio_bytes_list):
    # Create output directory
    os.makedirs("output_audio", exist_ok=True)
    
    # Save segments locally
    audio_files = []
    for idx, audio_bytes in enumerate(audio_bytes_list):
        output_path = f"output_audio/segment_{idx}.wav"
        with open(output_path, "wb") as f:
            f.write(audio_bytes)
        audio_files.append(output_path)
    
    # Merge audio files
    master_audio = AudioSegment.empty()
    for file in audio_files:
        master_audio += AudioSegment.from_wav(file)
    
    # Export final file
    master_output_path = "master_output.wav"
    master_audio.export(master_output_path, format="wav")
    return master_output_path

def main():
    # Load script data
    with open('scripts.json') as f:
        script_data = json.load(f)
    
    # Generate audio
    audio_bytes_list = generate_audio(script_data)
    
    # Merge and save final audio
    final_path = merge_audio(audio_bytes_list)
    
    print(f"Audio generation complete! Saved as {final_path}")

if __name__ == "__main__":
    main()