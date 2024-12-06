workers = 1


def init_model():
    from diffusers import AutoPipelineForText2Image
    import torch
    return AutoPipelineForText2Image.from_pretrained("stabilityai/sdxl-turbo", torch_dtype=torch.float16,
                                                     variant="fp16").to("cuda")


def generate_image(model, image_prompt, output_path, pbar=None):
    image = model(prompt=image_prompt, num_inference_steps=80, guidance_scale=3.5).images[0]
    image.save(output_path)
    return image

