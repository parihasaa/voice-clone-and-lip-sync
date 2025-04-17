# Voice Cloning and Lip Syncing with Tortoise TTS and Wav2Lip

This project integrates voice cloning using [Tortoise TTS](https://github.com/neonbjb/tortoise-tts) and lip-syncing using [Wav2Lip](https://github.com/Rudrabha/Wav2Lip) into a single Gradio interface. The user can input a reference audio and text to clone a voice, and optionally sync the generated audio to a video.

## Features

- Voice cloning using Tortoise TTS with reference audio and input text
- Lip-syncing the cloned voice to a face video using Wav2Lip
- Minimal Gradio-based interface for user interaction
- Example assets provided for quick testing

## Run on Kaggle

You can try this project directly on Kaggle without any local setup:

**[Open in Kaggle →]([(https://www.kaggle.com/code/parihasakreddy/voiceclone-lipsync-ipynb)](https://www.kaggle.com/code/parihasakreddy/voiceclone-lipsync-ipynb))**

**Notes:**
- Initial loading may take approximately 3 minutes.
- Use the files in the `assets/` directory to test the pipeline.
- Voice cloning typically takes 2–3 minutes for short text.
- Lip-syncing may not yield good results for very short voice samples. For best results, test lip-syncing with longer audio.
- Alternatively, lip-syncing can be tested independently using this notebook:  
  **[Wav2Lip public notebook →][(https://www.kaggle.com/USERNAME/wav2lip-notebook-link](https://www.kaggle.com/code/parihasakreddy/lipsync-only))**

## Usage

### Clone and run locally

```bash
git clone https://github.com/yourusername/voice-clone-lipsync.git
cd voice-clone-lipsync
pip install -r requirements.txt
python app.py
