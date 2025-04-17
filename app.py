import os
import torch
import shutil
import subprocess
import torchaudio
import gradio as gr
from tortoise.api import TextToSpeech
from tortoise.utils.audio import load_audio

# Constants
WORKING_DIR = "./workspace"
CLONED_VOICE_PATH = os.path.join(WORKING_DIR, "cloned_voice.wav")
OUTPUT_VIDEO_PATH = os.path.join(WORKING_DIR, "lip_synced_video.mp4")

# Initialize directories
os.makedirs(WORKING_DIR, exist_ok=True)
os.makedirs(os.path.join(WORKING_DIR, "temp"), exist_ok=True)
os.makedirs(os.path.join(WORKING_DIR, "results"), exist_ok=True)

# Initialize Tortoise TTS
tts = TextToSpeech()

def generate_voice_clone(audio_file, text, quality):
    """
    Clone voice using reference audio and text
    """
    try:
        if isinstance(audio_file, tuple):
            sample_rate, audio_data = audio_file
            torchaudio.save(CLONED_VOICE_PATH, torch.from_numpy(audio_data).float(), sample_rate)
        else:
            shutil.copy(audio_file, CLONED_VOICE_PATH)

        voice_samples = [load_audio(CLONED_VOICE_PATH, 22050)]
        gen = tts.tts_with_preset(text, voice_samples=voice_samples, preset=quality, diffusion_iterations=100)
        torchaudio.save(CLONED_VOICE_PATH, gen.squeeze(0).cpu(), 24000)

        return CLONED_VOICE_PATH, "✅ Voice cloned successfully!"
    except Exception as e:
        return None, f"❌ Error during voice cloning: {str(e)}"

def lip_sync(video_path):
    """
    Generate a lip-synced video using the cloned voice and input video
    """
    try:
        if not os.path.exists(CLONED_VOICE_PATH):
            return None, "⚠️ Please generate a cloned voice first!", None

        input_video_path = os.path.join(WORKING_DIR, "input_video.mp4")
        if isinstance(video_path, str) and os.path.exists(video_path):
            shutil.copy(video_path, input_video_path)
        elif isinstance(video_path, dict) and "name" in video_path:
            shutil.copy(video_path["name"], input_video_path)
        else:
            raise Exception("Invalid or missing video input.")

        temp_audio = os.path.join(WORKING_DIR, "temp", "converted_audio.wav")
        processed_video = os.path.join(WORKING_DIR, "temp", "processed_video.mp4")
        result_avi = os.path.join(WORKING_DIR, "temp", "result.avi")
        final_output = os.path.join(WORKING_DIR, "results", "lip_synced_output.mp4")

        subprocess.run(f"ffmpeg -y -i {CLONED_VOICE_PATH} -ar 16000 {temp_audio}", shell=True, check=True)
        subprocess.run(f"ffmpeg -y -i {input_video_path} -c:v libx264 -profile:v high -crf 20 -pix_fmt yuv420p {processed_video}", shell=True, check=True)

        wav2lip_cmd = f"""
        python Wav2Lip/inference.py \
            --checkpoint_path Wav2Lip/checkpoints/wav2lip_gan.pth \
            --face "{processed_video}" \
            --audio "{temp_audio}" \
            --outfile "{result_avi}" \
            --resize_factor 1 \
            --fps 25 \
            --face_det_batch_size 4 \
            --wav2lip_batch_size 16 \
            --nosmooth
        """
        subprocess.run(wav2lip_cmd, shell=True, check=True)

        subprocess.run(f"ffmpeg -y -i {result_avi} -vcodec libx264 -acodec aac {final_output}", shell=True, check=True)

        if os.path.exists(final_output):
            return final_output, "✅ Lip-sync completed!", CLONED_VOICE_PATH
        else:
            return None, "❌ Lip-sync failed: No output generated", None

    except subprocess.CalledProcessError as e:
        return None, f"❌ Subprocess failed: {e}", None
    except Exception as e:
        return None, f"❌ Error during lip sync: {str(e)}", None

# ─── Gradio Interface ─────────────────────────────────────────────────────────

with gr.Blocks(theme=gr.themes.Default(primary_hue="blue")) as demo:
    gr.Markdown("## 🎤 Voice Cloning + 🎬 Lip Sync Studio")
    
    with gr.Tab("1️⃣ Voice Cloning"):
        audio_input = gr.Audio(label="🎙️ Reference Audio", type="filepath")
        text_input = gr.Textbox(label="📝 Text to Synthesize")
        quality_input = gr.Dropdown(choices=["fast", "standard", "high_quality"], value="standard", label="⚙️ Quality Preset")
        clone_btn = gr.Button("✨ Clone Voice")
        clone_output_audio = gr.Audio(label="🔊 Cloned Voice Output")
        clone_status = gr.Textbox(label="Status")

        clone_btn.click(
            fn=generate_voice_clone,
            inputs=[audio_input, text_input, quality_input],
            outputs=[clone_output_audio, clone_status]
        )

    with gr.Tab("2️⃣ Lip Sync"):
        video_input = gr.Video(label="🎥 Upload Target Video")
        sync_btn = gr.Button("🎬 Generate Lip Sync")
        lip_output_video = gr.Video(label="📺 Lip-Synced Output")
        lip_status = gr.Textbox(label="Status")
        lip_voice_preview = gr.Audio(label="🔈 Used Voice")

        sync_btn.click(
            fn=lip_sync,
            inputs=[video_input],
            outputs=[lip_output_video, lip_status, lip_voice_preview]
        )

demo.launch(share=True)
