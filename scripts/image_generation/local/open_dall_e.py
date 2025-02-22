workers = 1


def init_model():
    import torch
    from diffusers import AutoPipelineForText2Image
    return AutoPipelineForText2Image.from_pretrained('dataautogpt3/OpenDalleV1.1',
                                                     torch_dtype=torch.float16).to('cuda')


def generate_image(model, image_prompt, output_path, pbar=None):
    image = model(image_prompt, num_inference_steps=20)["images"][0]
    image.save(output_path)
    return image


if __name__ == '__main__':
    prompt = "A whimsical and creative image depicting a hybrid creature that is a mix of a waffle and a hippopotamus, basking in a river of melted butter amidst a breakfast-themed landscape. It features the distinctive, bulky body shape of a hippo. However, instead of the usual grey skin, the creature's body resembles a golden-brown, crispy waffle fresh off the griddle. The skin is textured with the familiar grid pattern of a waffle, each square filled with a glistening sheen of syrup. The environment combines the natural habitat of a hippo with elements of a breakfast table setting, a river of warm, melted butter, with oversized utensils or plates peeking out from the lush, pancake-like foliage in the background, a towering pepper mill standing in for a tree.  As the sun rises in this fantastical world, it casts a warm, buttery glow over the scene. The creature, content in its butter river, lets out a yawn. Nearby, a flock of birds take flight"
    generate_image(prompt, "cat.png")
