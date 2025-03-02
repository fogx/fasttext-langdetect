import os
import fasttext
import requests
from typing import Dict, Union

# mute warning until 0.9.3 gets released
# https://github.com/facebookresearch/fastText/issues/1067
fasttext.FastText.eprint = lambda x: None

models = {"low_mem": None, "high_mem": None}
FTLANG_CACHE = os.getenv("FTLANG_CACHE", "/tmp/fasttext-langdetect")


def download_model(name):
    target_path = os.path.join(FTLANG_CACHE, name)
    if not os.path.exists(target_path):
        url = f"https://dl.fbaipublicfiles.com/fasttext/supervised-models/{name}"
        os.makedirs(FTLANG_CACHE, exist_ok=True)
        resp = requests.get(url)
        open(target_path, "wb").write(resp.content)
    return target_path


def get_or_load_model(low_memory=False):
    if low_memory:
        model = models.get("low_mem", None)
        if not model:
            model_path = download_model("lid.176.ftz")
            model = fasttext.load_model(model_path)
            models["low_mem"] = model
        return model
    else:
        model = models.get("high_mem", None)
        if not model:
            model_path = download_model("lid.176.bin")
            model = fasttext.load_model(model_path)
            models["high_mem"] = model
        return model


def detect(text: str, low_memory=False) -> Dict[str, Union[str, float]]:
    model = get_or_load_model(low_memory)
    labels, scores = model.predict(text)
    label = labels[0].replace("__label__", '')
    score = min(float(scores[0]), 1.0)
    return {
        "lang": label,
        "score": score,
    }
