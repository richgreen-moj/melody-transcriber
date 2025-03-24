import os
import subprocess
from music21 import converter, midi, stream, key, instrument, clef
from basic_pitch.inference import predict_and_save, Model
from basic_pitch import ICASSP_2022_MODEL_PATH


WORKING_DIR = "/app"

def transcribe_melody(input_audio):
    # Ensure paths are inside the working directory
    input_audio_path = os.path.join(WORKING_DIR, input_audio)
    output_dir = os.path.join(WORKING_DIR, "output")
    os.makedirs(output_dir, exist_ok=True)

    # Step 1: Run Demucs to separate vocals
    print("🔄 Running Demucs to separate vocals...")
    demucs_result = subprocess.run(
        ["python3", "-m", "demucs.separate", "-n", "htdemucs", "--two-stems=vocals", input_audio_path],
        capture_output=True,
        text=True
    )
    print(demucs_result.stdout)
    print(demucs_result.stderr)
    if demucs_result.returncode != 0:
        raise RuntimeError(f"Demucs failed: {demucs_result.stderr}")

    # Locate extracted vocals
    song_name = os.path.splitext(os.path.basename(input_audio))[0]
    vocals_path = os.path.join(WORKING_DIR, f"separated/htdemucs/{song_name}/vocals.wav")
    if not os.path.exists(vocals_path):
        raise FileNotFoundError(f"Vocals file not found: {vocals_path}")
    print(f"✅ Vocals file located: {vocals_path}")

    # Step 2: Convert vocals to MIDI using Basic Pitch
    print("🔄 Running Basic Pitch to convert vocals to MIDI...")

    # Load the model
    model = Model(ICASSP_2022_MODEL_PATH)

    # Call the function to process the audio and save outputs
    predict_and_save(
        audio_path_list=[vocals_path],
        output_directory=output_dir,
        model_or_model_path=model,
        save_midi=True,
        sonify_midi=False,
        save_model_outputs=False,
        save_notes=False,
        onset_threshold=0.6,
        frame_threshold=0.5,
        minimum_note_length=80,
        minimum_frequency=100,
        maximum_frequency=1500,
        melodia_trick=True
    )
    # basic_pitch_result = subprocess.run(
    #     ["basic-pitch", output_dir, vocals_path, 
    #         "--save-midi", 
    #         "--onset-threshold", "0.6", 
    #         "--frame-threshold", "0.5", 
    #         "--minimum-note-length", "80", 
    #         "--minimum-frequency", "100", 
    #         "--maximum-frequency", "1500", 
    #         "--model-serialization", "tf", 
    #         "--no-melodia"
    #     ],
    #     capture_output=True,
    #     text=True
    # )
    # print(basic_pitch_result.stdout)
    # print(basic_pitch_result.stderr)

    # Step 3: Tidy up the MIDI file
    print("🔄 Processing MIDI file...")
    midi_file = converter.parse("output/vocals_basic_pitch.mid")

    # 🎼 Detect Key Signature
    key_signature = midi_file.analyze('key')
    print(f"Detected Key: {key_signature}")

    # Assign the detected key to all parts
    for part in midi_file.parts:
        part.insert(0, key_signature)

    # 🎵 Quantize Notes (snap to nearest 16th note)
    for note in midi_file.flat.notes:
        note.quarterLength = round(note.quarterLength * 4) / 4  # Rounds to nearest 16th note

    # 🎹 Change Default MIDI Instrument to a Voice Sound
    # Iterate over parts and change the instrument
    for part in midi_file.parts:
        # Change to a new instrument (e.g., Acoustic Grand Piano = 1)
        new_instrument = instrument.instrumentFromMidiProgram(52)  # 52 = Choir Aahs 
        part.insert(0, new_instrument)

    # Save the cleaned-up MIDI
    midi_file.write("midi", fp="cleaned_output.mid")
    print("✅ MIDI file processed and saved as 'cleaned_output.mid'")

# Run the script from the command line
if __name__ == "__main__":
    import sys
    if len(sys.argv) < 2:
        print("Usage: python transcribe.py <audio_file>")
        sys.exit(1)
    
    transcribe_melody(sys.argv[1])