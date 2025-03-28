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

`docker run --rm -v $(pwd):/app melody-transcriber your_audio_file.mp3`