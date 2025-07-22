import os
import subprocess
import argparse
from mutagen import File
from mutagen.wave import WAVE
from mutagen.mp3 import MP3
import eyed3.mp3.headers as hdr
from groq import Groq
from pyannote.audio import Pipeline

# Initialize
client = Groq(api_key=os.getenv("GROQ_API_KEY"))
pipeline = Pipeline.from_pretrained("pyannote/speaker-diarization")
clean_audio_wav_file = "data/new_clean_audio.wav"
output_text_file = "data/output_file.txt"


def rebuild_audio(input_path: str, output_path: str) -> None:
    """
    Uses FFmpeg to convert a potentially malformed MP3 into a clean WAV file.
    This ensures no corrupt frames disrupt downstream processing.
    """
    cmd = [
        "ffmpeg",
        "-err_detect", "ignore_err",  # continue past frame errors
        "-i", input_path,  # input file
        "-acodec", "pcm_s16le",  # uncompressed 16-bit PCM
        "-ac", "1",  # mono channel
        "-ar", "16000",  # 16 kHz sample rate
        "-y", output_path  # overwrite output
    ]
    subprocess.run(cmd, check=True, capture_output=True)
    print(f"Rebuilt audio saved to '{output_path}'")


def main(audio_wav_file_name):
    # Transcribe audio with timestamped segments
    with open(audio_wav_file_name, "rb") as f:
        resp = client.audio.transcriptions.create(
            file=f,
            model="whisper-large-v3-turbo",
            response_format="verbose_json",
            timestamp_granularities=["segment"],
            temperature=0.0
        )

    transcript_segments = resp.segments  # Correct: use attribute access

    # Run diarization
    diarization = pipeline({"uri": "meeting", "audio": audio_wav_file_name})
    spk_segments = [
        {"start": turn.start, "end": turn.end, "speaker": label}
        for turn, _, label in diarization.itertracks(yield_label=True)
    ]

    # Align transcripts with speakers
    merged = []
    for seg in transcript_segments:
        seg_start = seg["start"]
        seg_end = seg["end"]
        overlaps = [
            (max(0, min(seg_end, sp["end"]) - max(seg_start, sp["start"])), sp["speaker"])
            for sp in spk_segments
        ]
        best_overlap, speaker = max(overlaps, default=(0, "SPEAKER_UNKNOWN"))
        merged.append({
            "start": seg_start,
            "end": seg_end,
            "text": seg["text"],
            "speaker": speaker
        })

    # Map speaker IDs to friendly names
    mapping = {"SPEAKER_00": "Speaker 1", "SPEAKER_01": "Speaker 2"}
    for m in merged:
        m["speaker_name"] = mapping.get(m["speaker"], m["speaker"])

    # Save to text file
    with open(output_text_file, "w", encoding="utf-8") as out:
        for m in merged:
            out.write(f'{m["speaker_name"]} : {m["text"]} \n')


def has_mp3_frame(fn):
    with open(fn, "rb") as f:
        _, header_int, _ = hdr.findHeader(f, 0)
    return bool(header_int)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Process MP3 or WAV files.")
    parser.add_argument("filename", help="Path to the audio file")
    args = parser.parse_args()
    file_name = args.filename
    print("Input Filename: ", file_name)

    audio = File(file_name)
    if isinstance(audio, MP3):
        print("Filetype is mp3")
        rebuild_audio(file_name, clean_audio_wav_file)
        main(clean_audio_wav_file)
    elif isinstance(audio, WAVE):
        print("Filetype is wav")
        main(file_name)
    elif has_mp3_frame(file_name):
        print("MP3 frames found but Mutagen couldn’t parse them — still processing as MP3")
        rebuild_audio(file_name, clean_audio_wav_file)
    else:
        print("Unsupported or unrecognized type")
