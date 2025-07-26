import os
import subprocess
import tempfile
import logging
import traceback
from typing import Optional
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
            "pyannote/speaker-diarization",
            use_auth_token=huggingface_token
        )
        logger.info("Speaker diarization pipeline loaded successfully")
except Exception as e:
    logger.error(f"Failed to load diarization pipeline: {str(e)}")
    pipeline = None


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


def transcribe_audio(audio_file_path: str) -> list:
    """
    Transcribe audio file using Groq Whisper API
    Returns list of transcript segments with timestamps
    """
    if not client:
        raise Exception("Groq client not initialized. "
                        "Please check your GROQ_API_KEY in the .env file.")

    try:
        with open(audio_file_path, "rb") as f:
            response = client.audio.transcriptions.create(
                file=f,
                model="whisper-large-v3-turbo",
                response_format="verbose_json",
                timestamp_granularities=["segment"],
                temperature=0.0
            )

        if hasattr(response, 'segments') and response.segments:
            logger.info(f"Transcription completed: {len(response.segments)} segments")
            return response.segments
        else:
            logger.warning("No segments found in transcription response")
            return []

    except Exception as e:
        logger.error(f"Transcription error: {str(e)}")
        raise Exception(f"Audio transcription failed: {str(e)}")


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
        diarization = pipeline({"uri": "conversation", "audio": audio_file_path})

        speaker_segments = [
            {"start": turn.start, "end": turn.end, "speaker": label}
            for turn, _, label in diarization.itertracks(yield_label=True)
        ]

        logger.info(f"Speaker diarization completed: {len(speaker_segments)} segments")
        return speaker_segments

    except Exception as e:
        logger.error(f"Speaker diarization error: {str(e)}")
        return []


def align_transcripts_with_speakers(transcript_segments: list, speaker_segments: list) -> list:
    """
    Align transcript segments with speaker segments
    Returns merged segments with speaker information
    """
    merged_segments = []

    for seg in transcript_segments:
        seg_start = seg.get("start", 0)
        seg_end = seg.get("end", 0)
        text = seg.get("text", "").strip()

        if not text:
            continue

        # Find best matching speaker based on time overlap
        best_speaker = "SPEAKER_UNKNOWN"
        max_overlap = 0

        for sp_seg in speaker_segments:
            overlap_start = max(seg_start, sp_seg["start"])
            overlap_end = min(seg_end, sp_seg["end"])
            overlap_duration = max(0, overlap_end - overlap_start)

            if overlap_duration > max_overlap:
                max_overlap = overlap_duration
                best_speaker = sp_seg["speaker"]

        merged_segments.append({
            "start": seg_start,
            "end": seg_end,
            "text": text,
            "speaker": best_speaker
        })

    return merged_segments


def map_speakers_to_roles(merged_segments: list) -> list:
    """
    Map speaker IDs to meaningful roles (Agent/Customer)
    Uses simple heuristics to determine roles
    """
    # Default mapping
    speaker_mapping = {
        "SPEAKER_00": "Agent",
        "SPEAKER_01": "Customer",
        "SPEAKER_02": "Customer",  # Fallback if more speakers detected
        "SPEAKER_UNKNOWN": "Speaker"
    }

    # Role detection based on content patterns
    agent_keywords = ['help', 'assist', 'support', 'service', 'solve', 'resolve', 'company', 'policy']
    customer_keywords = ['problem', 'issue', 'complaint', 'order', 'refund', 'cancel', 'disappointed']

    # Analyze content to improve speaker mapping
    speaker_content = {}
    for segment in merged_segments:
        speaker = segment["speaker"]
        text = segment["text"].lower()

        if speaker not in speaker_content:
            speaker_content[speaker] = []
        speaker_content[speaker].append(text)

    # Determine roles based on content analysis
    for speaker, texts in speaker_content.items():
        all_text = " ".join(texts)
        agent_score = sum(1 for keyword in agent_keywords if keyword in all_text)
        customer_score = sum(1 for keyword in customer_keywords if keyword in all_text)

        if agent_score > customer_score and speaker in ["SPEAKER_00", "SPEAKER_01"]:
            speaker_mapping[speaker] = "Agent"
        elif customer_score > agent_score and speaker in ["SPEAKER_00", "SPEAKER_01"]:
            speaker_mapping[speaker] = "Customer"

    # Apply mapping
    for segment in merged_segments:
        segment["speaker_name"] = speaker_mapping.get(segment["speaker"], segment["speaker"])

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

        # Step 1: Transcribe audio
        logger.info("[DEBUG] Starting transcription...")
        transcript_segments = transcribe_audio(processing_file_path)
        logger.info(f"[DEBUG] Transcript segments: {len(transcript_segments)}")

        if not transcript_segments:
            raise Exception("[DEBUG] No transcription segments generated")

        # Step 2: Perform speaker diarization
        logger.info("[DEBUG] Starting speaker diarization...")
        speaker_segments = perform_speaker_diarization(processing_file_path)
        logger.info(f"[DEBUG] Speaker segments: {len(speaker_segments)}")

        # Step 3: Align transcripts with speakers
        logger.info("[DEBUG] Aligning transcripts with speakers...")
        merged_segments = align_transcripts_with_speakers(transcript_segments, speaker_segments)

        # Step 4: Map speakers to roles
        logger.info("[DEBUG] Mapping speakers to roles...")
        final_segments = map_speakers_to_roles(merged_segments)

        # Step 5: Format as conversation text
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


# For backward compatibility and direct script usage
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