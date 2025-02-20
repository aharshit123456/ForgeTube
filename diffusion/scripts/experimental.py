# import torch
# # from llama_tts import LlamaTTS  # Assuming a LlamaTTS module
# from diffusers import StableDiffusionPipeline

# # Load the model
# pipe = StableDiffusionPipeline.from_pretrained("stabilityai/stable-diffusion-2-1")
# pipe.to("cuda")  # Use GPU for better performance

# # Load script
# with open("script.json", "r") as file:
#     script = json.load(file)

# # Generate images based on the script
# for frame in script["visual_script"]:
#     image = pipe(
#         prompt=frame["prompt"],
#         negative_prompt=frame["negative_prompt"],
#         guidance_scale=frame["guidance_scale"],
#         num_inference_steps=frame["steps"],
#         width=frame["width"],
#         height=frame["height"],
#         generator=torch.manual_seed(frame["seed"])
#     ).images[0]
    
#     output_file = f"image_{frame['timestamp'].replace(':', '')}.png"
#     image.save(output_file)
#     print(f"Saved {output_file}")