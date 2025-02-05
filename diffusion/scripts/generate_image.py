import modal
import json
import os
import time
from io import BytesIO

image = modal.Image.debian_slim().pip_install(
    "diffusers",
    "torch",
    "transformers",
    "accelerate"
)

app = modal.App(name="finalgen_app")

@app.function(image=image, gpu="A10G")
def generate_image(prompt, negative_prompt="", steps=50, guidance_scale=12, width=1024, height=576, seed=None):
    import torch
    from diffusers import StableDiffusionPipeline


# LOADS THE DIFFUSION PIPELINE

    pipe = StableDiffusionPipeline.from_pretrained("runwayml/stable-diffusion-v1-5", torch_dtype=torch.float16)
    pipe.to("cuda")

    generator = torch.Generator(device="cuda").manual_seed(seed) if seed else None

    image = pipe(
        prompt,
        negative_prompt=negative_prompt,
        num_inference_steps=steps,
        guidance_scale=guidance_scale,
        width=width,
        height=height,
        generator=generator
    ).images[0]

    img_byte_arr = BytesIO()
    image.save(img_byte_arr, format="PNG")
    img_byte_arr.seek(0)

    return img_byte_arr.getvalue()


# PATH TO JSON FILE

json_path = "scripts.json"
output_path = "imagedir/"
os.makedirs(output_path, exist_ok=True)


# PROVIDE SOURCE TEXT OR PROMPT IN JSON FILE

def main():
    # JSON Decoding Error Handling
    with open(json_path, "r", encoding="utf-8") as file:
        try:
            data = json.load(file)
        except json.JSONDecodeError:
            print("Error reading JSON file.")
            return
    # JSON Key Error Handling
    if "visual_script" not in data:
        print("Missing key in JSON.")
        return
    

# GENERATING THE IMAGES 

    with app.run():
        # Looping Through the Scenes
        for idx, scene in enumerate(data["visual_script"]):
            try:
                prompt = scene["prompt"]
                timestamp = scene.get("timestamp", f"{idx:03d}")
                negative_prompt = scene.get("negative_prompt", "")
                steps = scene.get("steps", 50)
                guidance_scale = scene.get("guidance_scale", 12)
                width = scene.get("width", 1024)
                height = scene.get("height", 576)
                seed = scene.get("seed", None)

                scene_id = timestamp.replace(":", "-")

                image_data = generate_image.remote(prompt, negative_prompt, steps, guidance_scale, width, height, seed)


# SAVING THE IMAGES IN THE OUTPUT DIRECTORY

                file_path = os.path.join(output_path, f"scene_{scene_id}.png")
                with open(file_path, "wb") as f:
                    f.write(image_data)

                print(f"Saved: {file_path}")

                time.sleep(2)

            except Exception as e:
                print(f"Error processing scene {idx}: {e}")

    print("Done.")

if __name__ == "__main__":
    main()
