import os
import re
import subprocess
import tempfile
import logging
import traceback
import soundfile as sf
from mutagen import File
from mutagen.mp4 import MP4
from mutagen.wave import WAVE
from mutagen.mp3 import MP3
import eyed3.mp3.headers as hdr
from groq import Groq
from pyannote.audio import Pipeline
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize clients
try:
    groq_api_key = os.getenv("GROQ_API_KEY")
    if not groq_api_key:
        logger.warning("GROQ_API_KEY not found in environment variables. "
                       "Transcription will not be available.")
        client = None
    else:
        client = Groq(api_key=groq_api_key)
        logger.info("Groq client initialized successfully")
except Exception as e:
    logger.error(f"Failed to initialize Groq client: {str(e)}")
    client = None

try:
    huggingface_token = os.getenv("HF_TOKEN")
    if not huggingface_token:
        logger.warning("HUGGINGFACE_TOKEN not found in environment variables. "
                       "Speaker diarization will not be available.")
        pipeline = None
    else:
        pipeline = Pipeline.from_pretrained(
            "pyannote/speaker-diarization-3.1",
            use_auth_token=huggingface_token
        )
        logger.info("Speaker diarization pipeline loaded successfully")
except Exception as e:
    logger.error(f"Failed to load diarization pipeline: {str(e)}")
    pipeline = None


# Filler word remover
def clean_text(text: str) -> str:
    FILLER_PATTERN = r'\b(um+|uh+|ah+|erm|hmm|you know|like)\b'
    text = re.sub(FILLER_PATTERN, '', text, flags=re.IGNORECASE)
    text = re.sub(r'\s{2,}', ' ', text).strip()
    return text


def rebuild_audio(input_path: str, output_path: str) -> None:
    """
    Convert audio file to clean WAV format using FFmpeg.
    Ensures compatibility with downstream processing.
    """
    try:
        cmd = [
            "ffmpeg",
            "-err_detect", "ignore_err",
            "-i", input_path,
            "-acodec", "pcm_s16le",
            "-ac", "1",
            "-ar", "16000",  # 16 kHz sample rate
            "-y", output_path
        ]

        result = subprocess.run(cmd, check=True, capture_output=True, text=True)
        logger.info(f"Audio rebuilt successfully: {output_path}")

    except subprocess.CalledProcessError as e:
        logger.error(f"FFmpeg error: {e.stderr}")
        raise Exception(f"Audio conversion failed: {e.stderr}")
    except FileNotFoundError:
        raise Exception("FFmpeg not found. Please install FFmpeg to process audio files.")


def has_mp3_frame(file_path: str) -> bool:
    """Check if file has valid MP3 frames"""
    try:
        with open(file_path, "rb") as f:
            _, header_int, _ = hdr.findHeader(f, 0)
        return bool(header_int)
    except:
        return False


def split_audio_to_segments(audio_file_path, speaker_segments):
    """Split audio into speaker turns based on diarization."""
    audio, sr = sf.read(audio_file_path)
    audio_segments = []
    for seg in speaker_segments:
        start_sample = int(seg['start'] * sr)
        end_sample = int(seg['end'] * sr)
        segment_audio = audio[start_sample:end_sample]
        audio_segments.append({
            "audio": segment_audio,
            "start": seg['start'],
            "end": seg['end'],
            "speaker": seg['speaker']
        })
    return audio_segments, sr


def transcribe_audio_only(audio_file_path: str) -> str:
    """
    Transcribe full audio file without diarization or analysis.
    Returns the raw transcription text.
    """
    if not client:
        raise Exception("Groq client not initialized. Please set GROQ_API_KEY in .env.")

    if not os.path.exists(audio_file_path):
        raise Exception(f"Audio file not found: {audio_file_path}")

    try:
        # Check audio format
        audio = File(audio_file_path)
        needs_conversion = True

        if isinstance(audio, WAVE):
            needs_conversion = False
        elif isinstance(audio, (MP3, MP4)) or has_mp3_frame(audio_file_path):
            needs_conversion = True
        else:
            logger.warning("[DEBUG] Unknown audio format, attempting conversion")

        processing_file_path = audio_file_path

        if needs_conversion:
            with tempfile.NamedTemporaryFile(delete=False, suffix='.wav') as temp_wav:
                temp_wav_path = temp_wav.name

            try:
                rebuild_audio(audio_file_path, temp_wav_path)
                processing_file_path = temp_wav_path
                logger.info("[DEBUG] Audio conversion completed for transcription")
            except Exception as e:
                logger.error(f"[DEBUG] Audio conversion failed: {str(e)}")
                processing_file_path = audio_file_path

        # Perform transcription on full file
        with open(processing_file_path, "rb") as f:
            response = client.audio.transcriptions.create(
                file=f,
                model="whisper-large-v3-turbo",
                response_format="verbose_json",
                temperature=0.0
            )

        if hasattr(response, "text"):
            text = response.text
            # Clean transcript text if available
            text = clean_text(text)
        elif hasattr(response, "segments"):
            text = " ".join(subseg["text"] for subseg in response.segments)
            text = clean_text(text)
        else:
            text = ""

        # Clean up temp file
        if needs_conversion and processing_file_path != audio_file_path:
            try:
                os.unlink(processing_file_path)
            except:
                pass

        if not text.strip():
            raise Exception("No transcription text generated from audio.")

        return text.strip()

    except Exception as e:
        logger.error(f"[DEBUG] transcribe_audio_only failed: {e}")
        logger.error(traceback.format_exc())
        raise


def save_transcript_file(conversation_id, utterances, summary=None, output_dir="/data/transcripts"):
    """
    Save a conversation to a text file.
    Includes:
      - Optional bullet-point summary at top
      - Speaker-labeled dialogue with timestamps
    """
    os.makedirs(output_dir, exist_ok=True)
    path = os.path.join(output_dir, f"{conversation_id}.txt")
    with open(path, "w", encoding="utf-8") as fh:
        # Write summary first if provided
        if summary:
            fh.write("=== Conversation Summary ===\n")
            for bullet in summary:
                fh.write(f"• {bullet.strip()}\n")
            fh.write("\n=== Detailed Transcript ===\n")
        else:
            fh.write("=== Detailed Transcript ===\n")
        # Write each utterance
        for u in utterances:
            ts = f"[{u.get('start',0):.2f}-{u.get('end',0):.2f}]"
            speaker = u.get('speaker', 'Unknown')
            text = clean_text(u.get('text', ''))
            fh.write(f"{ts} {speaker}: {text}\n")
    return path


def transcribe_speaker_segments(audio_file_path, speaker_segments):
    """
    For each diarization segment, transcribe the corresponding audio and assign it directly to the speaker.
    """
    audio_segments, sr = split_audio_to_segments(audio_file_path, speaker_segments)
    results = []

    for seg in audio_segments:
        # Save segment to temp WAV file
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp_wav:
            sf.write(tmp_wav, seg["audio"], sr, format='WAV')
            temp_name = tmp_wav.name

        # Now the file handle is closed; re-open for reading
        try:
            with open(temp_name, "rb") as f:
                response = client.audio.transcriptions.create(
                    file=f,
                    model="whisper-large-v3-turbo",
                    response_format="verbose_json",
                    temperature=0.0
                )
                # Extract text from response
                if hasattr(response, "text"):
                    text = response.text
                elif hasattr(response, "segments"):
                    text = " ".join(subseg["text"] for subseg in response.segments)
                else:
                    text = ""
            results.append({
                "start": seg["start"],
                "end": seg["end"],
                "text": text.strip(),
                "speaker": seg["speaker"]
            })
        finally:
            os.unlink(temp_name)  # cleanup temp file after processing

    return results


def perform_speaker_diarization(audio_file_path: str) -> list:
    """
    Perform speaker diarization using pyannote.audio
    Returns list of speaker segments
    """
    if not pipeline:
        logger.warning("Speaker diarization pipeline not available. "
                       "Please check your HUGGINGFACE_TOKEN in the .env file.")
        return []

    try:
        diarization = pipeline({"uri": "conv", "audio": audio_file_path}, num_speakers=2)

        speaker_segments = [
            {"start": turn.start, "end": turn.end, "speaker": label}
            for turn, _, label in diarization.itertracks(yield_label=True)
        ]

        logger.info(f"Speaker diarization completed: {len(speaker_segments)} segments")
        return speaker_segments

    except Exception as e:
        logger.error(f"Speaker diarization error: {str(e)}")
        return []


def map_speakers_to_roles_enhanced(merged_segments: list) -> list:
    speaker_stats = {}
    agent_keywords = ['help', 'assist', 'support', 'company', 'policy', 'thank you for calling']  # expand this
    customer_keywords = ['problem', 'issue', 'my order', 'I need', 'complaint', 'refund']

    for seg in merged_segments:
        speaker = seg["speaker"]
        text = seg["text"].lower()
        if speaker not in speaker_stats:
            speaker_stats[speaker] = {"text": [], "duration": 0, "count": 0, "agent_score": 0, "customer_score": 0}
        speaker_stats[speaker]["text"].append(text)
        speaker_stats[speaker]["duration"] += seg["end"] - seg["start"]
        speaker_stats[speaker]["count"] += 1
        speaker_stats[speaker]["agent_score"] += sum(1 for k in agent_keywords if k in text)
        speaker_stats[speaker]["customer_score"] += sum(1 for k in customer_keywords if k in text)

    # Determine first speaker
    first_speaker = merged_segments[0]["speaker"]

    scores = []
    for sp, stat in speaker_stats.items():
        score = (
            stat["agent_score"] - stat["customer_score"],
            sp == first_speaker,  # is first speaker
            stat["duration"],  # total speaking time
        )
        scores.append((sp, score))

    # Heuristic: Agent usually has more agent_score, speaks first, and/or speaks longer
    scores_sorted = sorted(scores, key=lambda x: (x[1][0], x[1][1], x[1][2]), reverse=True)
    if len(scores_sorted) > 1:
        agent_id = scores_sorted[0][0]
        customer_id = scores_sorted[1][0]
    else:
        agent_id = scores_sorted[0][0]
        customer_id = agent_id  # fallback

    speaker_mapping = {
        agent_id: "Agent",
        customer_id: "Customer"
    }

    for seg in merged_segments:
        seg["speaker_name"] = speaker_mapping.get(seg["speaker"], seg["speaker"])

    return merged_segments


def format_conversation_text(merged_segments: list) -> str:
    """
    Format merged segments into conversation text format
    """
    conversation_lines = []

    for segment in merged_segments:
        speaker = segment["speaker_name"]
        text = segment["text"].strip()

        if text:  # Only add non-empty texts
            conversation_lines.append(f"{speaker}: {text}")

    return "\n".join(conversation_lines)


def process_audio_file(audio_file_path: str) -> str:
    try:
        logger.info(f"[DEBUG] Starting audio processing for: {audio_file_path}")

        # Validate file exists
        if not os.path.exists(audio_file_path):
            raise Exception(f"Audio file not found: {audio_file_path}")

        # Check if file needs conversion to WAV
        audio = File(audio_file_path)
        needs_conversion = True

        if isinstance(audio, WAVE):
            needs_conversion = False
        elif isinstance(audio, (MP3, MP4)) or has_mp3_frame(audio_file_path):
            needs_conversion = True
        else:
            logger.warning("[DEBUG] Unknown audio format, attempting conversion")

        processing_file_path = audio_file_path

        if needs_conversion:
            with tempfile.NamedTemporaryFile(delete=False, suffix='.wav') as temp_wav:
                temp_wav_path = temp_wav.name

            try:
                rebuild_audio(audio_file_path, temp_wav_path)
                processing_file_path = temp_wav_path
                logger.info("[DEBUG] Audio conversion completed")
            except Exception as e:
                logger.error(f"[DEBUG] Audio conversion failed: {str(e)}")
                processing_file_path = audio_file_path

        # Step 1: Perform speaker diarization
        logger.info("[DEBUG] Starting speaker diarization...")
        speaker_segments = perform_speaker_diarization(processing_file_path)
        logger.info(f"[DEBUG] Speaker segments: {len(speaker_segments)}")

        if not speaker_segments:
            raise Exception("[DEBUG] No speaker segments generated")

        # Step 2: Transcribe each speaker segment separately
        logger.info("[DEBUG] Starting speaker-specific transcription...")
        merged_segments = transcribe_speaker_segments(processing_file_path, speaker_segments)
        logger.info(f"[DEBUG] Speaker-attributed segments: {len(merged_segments)}")

        # Step 3: Map speakers to roles
        logger.info("[DEBUG] Mapping speakers to roles...")
        final_segments = map_speakers_to_roles_enhanced(merged_segments)

        # Step 4: Format as conversation text
        logger.info("[DEBUG] Formatting conversation text...")
        conversation_text = format_conversation_text(final_segments)

        logger.debug(f"[DEBUG] Final conversation text preview:\n{conversation_text[:500]}...")

        # Clean up temporary file if created
        if needs_conversion and processing_file_path != audio_file_path:
            try:
                os.unlink(processing_file_path)
            except:
                logger.warning("[DEBUG] Failed to delete temp file")

        if not conversation_text.strip():
            raise Exception("[DEBUG] No conversation text generated from audio")

        logger.info(f"[DEBUG] Audio processing completed successfully. Generated {len(final_segments)} utterances.")
        return conversation_text

    except Exception as e:
        logger.error(f"[DEBUG] process_audio_file failed: {e}")
        logger.error(traceback.format_exc())
        raise


def main(audio_file_name: str, output_text_file: str = "output_conversation.txt"):
    """
    Process audio file and save conversation to text file
    """
    try:
        conversation_text = process_audio_file(audio_file_name)

        # Save to output file
        with open(output_text_file, "w", encoding="utf-8") as out_file:
            out_file.write(conversation_text)

        logger.info(f"Conversation saved to: {output_text_file}")
        print(f"Processing completed! Conversation saved to: {output_text_file}")

    except Exception as e:
        logger.error(f"Processing failed: {str(e)}")
        print(f"Error: {str(e)}")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Process audio files to extract conversation text")
    parser.add_argument("filename", help="Path to the audio file")
    parser.add_argument("-o", "--output", default="output_conversation.txt", help="Output text file path")

    args = parser.parse_args()

    print(f"Processing audio file: {args.filename}")
    main(args.filename, args.output)
