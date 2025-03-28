import os
import subprocess
import json
from music21 import converter, midi, stream, key, instrument, clef
from basic_pitch.inference import predict_and_save, Model
from basic_pitch import ICASSP_2022_MODEL_PATH
from pydub import AudioSegment


WORKING_DIR = "/app"

def load_config(config_path):
    """Load settings from a JSON configuration file."""
    with open(config_path, "r") as f:
        return json.load(f)

def transcribe_melody(input_audio, config):
    # Ensure paths are inside the working directory
    input_audio_path = os.path.join(WORKING_DIR, input_audio)
    song_name = os.path.splitext(os.path.basename(input_audio))[0]
    output_dir = os.path.join(WORKING_DIR, "output", song_name)
    os.makedirs(output_dir, exist_ok=True)

    # Step 1: Run Demucs to separate vocals
    print("🔄 Running Demucs to separate vocals...")
    demucs_result = subprocess.run(
        ["python3", "-m", "demucs.separate", "-n", "htdemucs", "--two-stems=vocals", input_audio_path],
        text=True
    )
    print(demucs_result.stdout)
    print(demucs_result.stderr)
    if demucs_result.returncode != 0:
        raise RuntimeError(f"Demucs failed: {demucs_result.stderr}")

    # Locate extracted vocals
    vocals_path = os.path.join(WORKING_DIR, f"separated/htdemucs/{song_name}/vocals.wav")
    if not os.path.exists(vocals_path):
        raise FileNotFoundError(f"Vocals file not found: {vocals_path}")
    print(f"✅ Vocals file located: {vocals_path}")

    # Convert vocals to mono
    print("🔄 Converting vocals to mono...")
    vocals_audio = AudioSegment.from_file(vocals_path)
    vocals_audio = vocals_audio.set_channels(1)  # Set to mono
    mono_vocals_path = os.path.join(output_dir, "vocals_mono.wav")
    vocals_audio.export(mono_vocals_path, format="wav")
    print(f"✅ Vocals converted to mono and saved as: {mono_vocals_path}")

    # Update the path to use the mono file
    vocals_path = mono_vocals_path

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
        onset_threshold=config["onset_threshold"],
        frame_threshold=config["frame_threshold"],
        minimum_note_length=config["minimum_note_length"],
        minimum_frequency=config["minimum_frequency"],
        maximum_frequency=config["maximum_frequency"],
        melodia_trick=config["melodia_trick"]
    )

    # Step 3: Tidy up the MIDI file
    print("🔄 Processing MIDI file...")
    midi_file = converter.parse(os.path.join(output_dir, "vocals_mono_basic_pitch.mid"))

    # 🎼 Detect Key Signature
    key_signature = midi_file.analyze('key')
    print(f"Detected Key: {key_signature}")

    # Assign the detected key to all parts
    for part in midi_file.parts:
        part.insert(0, key_signature)

    # # 🎵 Quantize Notes (snap to nearest 16th note)
    # for note in midi_file.flat.notes:
    #     note.quarterLength = round(note.quarterLength * 4) / 4  # Rounds to nearest 16th note

    # 🎹 Change Default MIDI Instrument to a Voice Sound
    # Iterate over parts and change the instrument
    for part in midi_file.parts:
        # Change to a new instrument (e.g., Acoustic Grand Piano = 1)
        new_instrument = instrument.instrumentFromMidiProgram(52)  # 52 = Choir Aahs 
        part.insert(0, new_instrument)

    # Save the cleaned-up MIDI
    cleaned_midi_path = os.path.join(output_dir, f"{song_name}.mid")
    midi_file.write("midi", fp=cleaned_midi_path)
    print("✅ MIDI file processed and saved as:", cleaned_midi_path)

# Run the script from the command line
if __name__ == "__main__":
    import sys
    if len(sys.argv) < 3:
        print("Usage: python transcribe.py <audio_file> <config_file>")
        sys.exit(1)

    input_audio = sys.argv[1]
    config_file = sys.argv[2]

    # Load configuration
    config = load_config(config_file)

    # Run transcription
    transcribe_melody(input_audio, config)