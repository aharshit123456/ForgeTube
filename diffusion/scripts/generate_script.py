import modal
from transformers import AutoModelForCausalLM, AutoTokenizer
import torch
import json
import os 

# Define the Modal image with required libraries
image = modal.Image.debian_slim().pip_install(
    "torch", 
    "transformers"
)

# Create or reference a persistent Modal Volume
script_volume = modal.Volume.from_name("script_storage", create_if_missing=True)

# Create the Modal app
app = modal.App(name="huggingface_textgen_app")

@app.cls(image=image, gpu="A100", timeout=3600, volumes={"/mnt/volume": script_volume},secrets=[modal.Secret.from_name("huggingface-secret")])
class TextGenerator:
    def __init__(self):  # Fixed method name from _init_ to __init__
        """Initialize model, tokenizer, and system prompt."""
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        model_name = "meta-llama/Llama-3.1-8B"
        self.use_auth_token=os.environ["HF_TOKEN"]
        # Load tokenizer and model
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.model = AutoModelForCausalLM.from_pretrained(model_name).to(self.device)
        
        # Store system prompt as an instance variable
        self.system_prompt = """You are a professional video script generator. 
Generate only and only JSON output strictly following this structure:
{
    "topic": "Topic Name",
    "description": "description of the video",
    "audio_script": [{
        "timestamp": "00:00",
        "text": "Narration text",
        "speaker": "default|narrator_male|narrator_female",
        "speed": 0.9-1.1,
        "pitch": 0.9-1.2,
        "emotion": "neutral|serious|dramatic|mysterious|informative"
    }],
    "visual_script": [{
        "timestamp_start": "00:00",
        "timestamp_end": "00:05",
        "prompt": "Detailed Stable Diffusion prompt",
        "negative_prompt": "Low quality elements to avoid",
        "style": "realistic|cinematic|hyperrealistic|fantasy|scientific",
        "guidance_scale": 11.0-14.0,
        "steps": 50-100,
        "seed": 6 digit integer,
        "width": 1024,
        "height": 576
    }]
}
example 1:-
{
  "topic": "Hot Wheels: The Ultimate Collector\u2019s Guide",
  "description": "A comprehensive guide to Hot Wheels history, rare models, and future designs.",
  "audio_script": [
    {
      "timestamp": "00:00",
      "text": "Welcome to the world of Hot Wheels, where speed meets style. From its humble beginnings in the 1960s to its current status as a global phenomenon, Hot Wheels has captured the hearts of millions.",
      "speaker": "narrator_male",
      "speed": 1.0,
      "pitch": 1.0,
      "emotion": "enthusiastic"
    },
    {
      "timestamp": "00:05",
      "text": "In its early days, Hot Wheels was all about innovation. The first cars were designed by none other than the legendary Alec Issigonis, who also created the Mini Cooper.",
      "speaker": "narrator_male",
      "speed": 0.9,
      "pitch": 1.0,
      "emotion": "informative"
    },
    {
      "timestamp": "00:10",
      "text": "But it's not just about speed; it's also about rare models that make collectors go wild. Like the '66 Chevrolet Corvette, one of the most sought-after Hot Wheels cars ever made.",
      "speaker": "narrator_female",
      "speed": 1.1,
      "pitch": 1.0,
      "emotion": "excited"
    },
    {
      "timestamp": "00:15",
      "text": "And let's not forget the future of Hot Wheels! With designers pushing the boundaries of creativity, we can expect to see even more mind-blowing models in the years to come.",
      "speaker": "narrator_male",
      "speed": 1.0,
      "pitch": 1.0,
      "emotion": "enthusiastic"
    },
    {
      "timestamp": "00:20",
      "text": "From its humble beginnings to its current status as a global phenomenon, Hot Wheels has captured the hearts of millions. Join us next time for more fun facts and insights into this beloved toy brand.",
      "speaker": "narrator_female",
      "speed": 1.0,
      "pitch": 1.0,
      "emotion": "informative"
    }
  ],
  "visual_script": [
    {
      "timestamp_start": "00:00",
      "timestamp_end": "00:05",
      "prompt": "A vintage-style illustration of a Hot Wheels car on a track, with the words 'Hot Wheels' emblazoned across the top. The background is a warm, nostalgic color.",
      "negative_prompt": "blurry, distorted perspective",
      "style": "cinematic",
      "guidance_scale": 8.0,
      "steps": 60,
      "seed": 654321,
      "width": 1024,
      "height": 576
    },
    {
      "timestamp_start": "00:05",
      "timestamp_end": "00:10",
      "prompt": "A detailed, realistic shot of the '66 Chevrolet Corvette, with its sleek design and bright colors. The background is a deep blue to emphasize the car's presence.",
      "negative_prompt": "bad lighting, motion blur",
      "style": "cinematic",
      "guidance_scale": 8.5,
      "steps": 75,
      "seed": 222333,
      "width": 1024,
      "height": 576
    },
    {
      "timestamp_start": "00:10",
      "timestamp_end": "00:15",
      "prompt": "A futuristic, stylized illustration of a Hot Wheels car in mid-air, with neon lights and bold colors. The background is a deep black to emphasize the car's movement.",
      "negative_prompt": "blurry, cartoonish",
      "style": "cinematic",
      "guidance_scale": 9.0,
      "steps": 90,
      "seed": 987654,
      "width": 1024,
      "height": 576
    },
    {
      "timestamp_start": "00:15",
      "timestamp_end": "00:20",
      "prompt": "A wide-angle shot of a Hot Wheels car track, with multiple cars racing around the bend. The background is a warm, sunny color to emphasize the fun and excitement.",
      "negative_prompt": "bad lighting, motion blur",
      "style": "cinematic",
      "guidance_scale": 8.0,
      "steps": 60,
      "seed": 654321,
      "width": 1024,
      "height": 576
    }
  ]
} ensure audio and visual scripts are in sync
"""

    @modal.method()
    def generate(self, user_prompt: str, max_length: int = 5000) -> str:
        """Generate text based on the system prompt combined with user input."""
        # Use self.system_prompt instead of system_prompt
        full_prompt = f"{self.system_prompt}\n\n{user_prompt}"
        inputs = self.tokenizer(full_prompt, return_tensors="pt").to(self.device)

        outputs = self.model.generate(
            **inputs,
            max_length=max_length,
            num_return_sequences=1,
            do_sample=True,
            temperature=0.7,
            top_p=0.9
        )

        return self.tokenizer.decode(outputs[0], skip_special_tokens=True)
    
    @modal.method()
    def save_to_json(self, generated_text: str, filename: str = "generated_script.json") -> None:
        """Save generated script to a JSON file in Modal Volume."""
        try:
            parsed_json = json.loads(generated_text)
        except json.JSONDecodeError:
            parsed_json = {"script": generated_text}
        
        file_path = f"/mnt/volume/{filename}"
        with open(file_path, 'w') as f:
            json.dump(parsed_json, f, indent=4)
        
        # Commit changes to make sure the file is saved in the Volume
        script_volume.commit()
        print(f"Script saved to {file_path}")

    @modal.method()
    def read_from_json(self, filename: str = "generated_script.json") -> dict:
        """Retrieve saved JSON script from Modal Volume."""
        file_path = f"/mnt/volume/{filename}"
        
        try:
            with open(file_path, 'r') as f:
                content = json.load(f)
            return content
        except FileNotFoundError:
            return {"error": "File not found"}
    
# Entry point to run locally
@app.local_entrypoint()
def main():
    generator = TextGenerator()
    
    # Provide only the unique user instructions; the system prompt is already set
    user_prompt = """Generate a 60-second video script about: neural networks
Key Points: 'Comprehensive coverage'
- At least 6 segments (5-10 second intervals)
- Engaging and scientifically accurate narration
- Cinematic visuals with detailed prompts"""
    
    result = generator.generate.remote(user_prompt)
    
    print("\nGenerated Text:")
    print(result)

    # Save the generated script to a JSON file in the Volume
    generator.save_to_json.remote(result, "generated_scripts.json")
