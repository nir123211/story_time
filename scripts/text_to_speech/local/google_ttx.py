from gtts import gTTS


def init_model():
    return


def generate_speech(model, text, output_path, pbar=None):
    tts = gTTS(text, 'com')
    tts.save(output_path)
    if pbar:
        pbar.update(1)


if __name__ == '__main__':
    generate_speech(None, "hello!", "hello.mp3")