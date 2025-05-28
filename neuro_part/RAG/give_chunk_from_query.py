import json
import chromadb
import torch
import torch.nn.functional as F
from transformers import AutoTokenizer, AutoModel

DB_PATH = "./chroma_db"

chroma_client = chromadb.PersistentClient(path=DB_PATH)
collection = chroma_client.get_or_create_collection(name="documents")

tokenizer = AutoTokenizer.from_pretrained("ai-forever/ru-en-RoSBERTa")
model = AutoModel.from_pretrained("ai-forever/ru-en-RoSBERTa").to("cuda" if torch.cuda.is_available() else "cpu")
model.eval()


def vectorize_query(query_text) -> list:
    """
    Векторизует один текстовый запрос (без сохранения в БД).
    """

    tokenized_inputs = tokenizer(query_text, max_length=32, padding=True,
                                 truncation=True, return_tensors="pt").to(model.device)

    with torch.no_grad():
        outputs = model(**tokenized_inputs)

    embeddings = outputs.last_hidden_state[:, 0]
    embeddings = F.normalize(embeddings, p=2, dim=1)
    return embeddings.cpu().tolist()[0]


def find_similar_chunks(query_text, top_k=7) -> list:
    """
    Находит похожие чанки в ChromaDB по заданному тексту.
    """
    query_vector = vectorize_query(query_text)

    results = collection.query(query_embeddings=[query_vector], n_results=top_k)

    chunks = []

    for i, (chunk_text, distance) in enumerate(zip(results["metadatas"][0], results["distances"][0])):
        chunks.append(chunk_text['text'])

    return chunks




# Код будет запускаться при запуске именно этого файла, удобнее для тестирования
if __name__ == '__main__':
    query = 'кочевники'  # запрос от пользователя
    find_similar_chunks(query)