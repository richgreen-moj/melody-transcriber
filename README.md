# Melody Transcriber
An app to transcribe the melody from audio files and convert to MIDI for import to DAW or music notation software.

This leverages various other tools including:
- [demucs](https://github.com/facebookresearch/demucs) - for extracting the vocal stem from your audio
- [basic-pitch](https://github.com/spotify/basic-pitch) - for converting the audio to MIDI
- [music21](https://github.com/cuthbertLab/music21) - for extra MIDI processing

You can  feed the app any audio file and it will create a MIDI file based on the vocal stem of the track.

# Usage

Build the container image e.g.

`docker build -t melody-transcriber`

Then run the container specifying an audio file of your choice e.g.

`docker run --rm -v $(pwd):/app melody-transcriber your_audio_file.mp3 config.json`

The `config.json` file can be amended as required to alter the settings of basic-pitch which converts the audio to MIDI.

- `frame_threshold`: This sets the confidence threshold for detecting whether a frame contains a note. Lowering this value makes the model more lenient, allowing it to detect more notes (even less confident ones).

- `onset_threshold`: This determines how easily a note can be split into two. Lowering this value makes the model more sensitive to note onsets, which can help detect shorter or overlapping notes.

- `minimum_note_length`: This sets the minimum duration for a note to be considered valid. Lowering this value allows shorter notes to be detected.

- `minimum_frequency` and `maximum_frequency`: These parameters define the frequency range for valid notes. Expanding this range can help capture very low or very high notes that might be missed.

- `melodia_trick`: This heuristic focuses on extracting the most prominent melody. Enabling it can help in melody-dominant tracks (e.g., vocals or lead instruments).
