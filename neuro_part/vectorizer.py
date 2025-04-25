import json
from RAG.chunk_creater import  text_to_chunks
import torch
import torch.nn.functional as F
from torch.utils.data import DataLoader
from transformers import AutoTokenizer, AutoModel
import chromadb

tokenizer = AutoTokenizer.from_pretrained("ai-forever/ru-en-RoSBERTa")
model = AutoModel.from_pretrained("ai-forever/ru-en-RoSBERTa")

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
model = model.to(device)
torch.cuda.empty_cache()

DB_PATH = "RAG/chroma_db"


def vectorize_chunks(chunks: list, pooling_method="mean", batch_size=16) -> list:
    """
    Преобразует текстовые чанки в векторы, используя трансформер.
    """
    all_vectors = []
    dataloader = DataLoader(chunks, batch_size=batch_size, shuffle=False)

    for batch in dataloader:
        tokenized_inputs = tokenizer(batch, max_length=32, padding=True,
                                     truncation=True, return_tensors="pt").to(device)

        with torch.no_grad():
            outputs = model(**tokenized_inputs)

        if pooling_method == "mean":
            mask = tokenized_inputs["attention_mask"]
            embeddings = (outputs.last_hidden_state * mask.unsqueeze(-1)).sum(dim=1) / mask.sum(dim=1, keepdim=True)
        else:
            embeddings = outputs.last_hidden_state[:, 0]

        embeddings = F.normalize(embeddings, p=2, dim=1)
        all_vectors.extend(embeddings.cpu().tolist())

    return all_vectors


def save_chunks_with_vectors(text, db_path=DB_PATH) -> None:
    """
    Разбивает текст на чанки, векторизует их и сохраняет в ChromaDB.
    """

    chroma_client = chromadb.PersistentClient(path=db_path)
    collection = chroma_client.get_or_create_collection(name="documents")

    chunks = text_to_chunks(text)

    vectors = vectorize_chunks(chunks)
    chunk_ids = [f"chunk_{i}" for i in range(len(chunks))]

    collection.add(
        ids=chunk_ids,
        embeddings=vectors,
        metadatas=[{"text": chunk} for chunk in chunks]
    )

    config = {"db_path": db_path}
    with open("RAG/config.json", "w", encoding="utf-8") as f:
        json.dump(config, f)

def clear_db(db_path=DB_PATH) -> None:
    """
    Очищает коллекцию документов в базе данных ChromaDB.
    """
    chroma_client = chromadb.PersistentClient(path=db_path)
    collection = chroma_client.get_or_create_collection(name="documents")
    collection.delete(where={})  # Удаляет все документы без условий


# При запуске именно этого файла будет запускаться сохранение векторов 
if __name__ == '__main__':
    file_path = r""  # Замените на путь к файлу
    save_chunks_with_vectors(file_path)
