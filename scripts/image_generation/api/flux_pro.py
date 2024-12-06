import replicate

from misc.keys import replicate_key

workers = 4


def init_model():
    return replicate.Client(replicate_key)


def generate_image(model, image_prompt, output_path, pbar=None):
    output = model.run(
        "black-forest-labs/flux-1.1-pro",
        input={
            "prompt": image_prompt,
            "aspect_ratio": "1:1",
            "output_format": "png",
            "output_quality": 80,
            "safety_tolerance": 2,
            "prompt_upsampling": True
        }
    )

    with open(output_path, "wb") as file:
        file.write(output.read())

    if pbar:
        pbar.update(1)


if __name__ == '__main__':
    prompt = ("a mix of european and iraqi young woman, she has big cheeks and nose, wearing round glasses with thin, metallic rims. Her skin has a natural, smooth complexion, dotted with a few freckles that add character to her face. Her expressive, almond-shaped eyes peer out behind the lenses of her glasses. Her dark, straight hair is tied back loosely, leaving a few strands framing her face.")
    model = init_model()
    generate_image(model, prompt, "maayan.png")

