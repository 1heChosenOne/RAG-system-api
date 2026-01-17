import numpy as np
from utils import emb_model


def np_embed_texts(texts):
    return np.array(emb_model.encode(texts), dtype='float32')

def embed_text(text):
    return emb_model.encode([text]).astype("float32")