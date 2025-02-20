import modal
from io import BytesOS

image = modal.Image.debian_slim().pip_install(
    "torch",
    "torchaudio",
    "numpy",
    "torchvision",
    "bitsandbytes",
    "xcodec2",
    "huggingface_hub",
    "transformers",
    "tqdm",
)

app = modal.App(name="llasa_tts")

@app.function(image=image, gpu="A10G")
def load_model():
    from huggingface_hub import snapshot_download
    # snapshot download faster than normal download since its multiworker
    snapshot_download(repo_id="srinivasbilla/llasa-3b", local_dir="/content/srinivasbilla/llasa-3b")
    snapshot_download(repo_id="srinivasbilla/xcodec2", local_dir="/content/srinivasbilla/xcodec2")
    snapshot_download(repo_id="openai/whisper-large-v3-turbo", local_dir="/content/openai/whisper-large-v3-turbo")