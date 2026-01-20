import faiss
import numpy as np
from pathlib import Path


def write_index(owner_id, file_id, embeddings, ids):
    embedding_dim = embeddings.shape[1]
    index = faiss.IndexFlatL2(embedding_dim)
    index = faiss.IndexIDMap(index)
    index.add_with_ids(np.array(embeddings, dtype='float32'), np.array(ids, dtype='int64'))

    dir = Path("data/users") / f"user_{owner_id}"
    dir.mkdir(parents=True, exist_ok=True)
    index_path = dir / f"index_faiss_{file_id}.faiss"
    faiss.write_index(index, str(index_path))
    
def index_load(faiss_path):
    return faiss.read_index(str(faiss_path))

def index_search(index, question_embedding):
    d,i = index.search(question_embedding, k=4)
    return i