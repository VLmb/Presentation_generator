import json
from RAG.chunk_creater import text_to_chunks
import torch
import torch.nn.functional as F
from torch.utils.data import DataLoader
from transformers import AutoTokenizer, AutoModel
import chromadb
from loguru import logger
import sys

# Настройка логгера
logger.remove()
logger.add(sys.stderr, level="INFO")
logger.add("RAG/logs/vectorization.log", rotation="1 MB", compression="zip")

# Настройка векторизатора
logger.info("Загрузка токенизатора и модели...")
tokenizer = AutoTokenizer.from_pretrained("ai-forever/ru-en-RoSBERTa")
model = AutoModel.from_pretrained("ai-forever/ru-en-RoSBERTa")

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
model = model.to(device)
torch.cuda.empty_cache()
logger.info(f"Модель загружена и перемещена на устройство: {device}")

DB_PATH = "RAG/chroma_db"
chroma_client = chromadb.PersistentClient(path=DB_PATH)
collection = chroma_client.get_or_create_collection(name="documents")


def vectorize_chunks(chunks: list, pooling_method="mean", batch_size=16) -> list:
    """
    Преобразует текстовые чанки в векторы, используя трансформер.
    """
    logger.info(f"Начинается векторизация {len(chunks)} чанков...")
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

    logger.info("Векторизация завершена.")
    return all_vectors


def save_chunks_with_vectors(text, db_path=DB_PATH) -> None:
    """
    Разбивает текст на чанки, векторизует их и сохраняет в ChromaDB.
    """
    try:
        logger.info("Инициализация клиента ChromaDB...")
        chroma_client = chromadb.PersistentClient(path=db_path)
        collection = chroma_client.get_or_create_collection(name="documents")

        logger.info("Разбиение текста на чанки...")
        chunks = text_to_chunks(text)
        logger.info(f"Чанков получено: {len(chunks)}")

        vectors = vectorize_chunks(chunks)
        chunk_ids = [f"chunk_{i}" for i in range(len(chunks))]

        logger.info("Добавление чанков и векторов в коллекцию...")
        collection.add(
            ids=chunk_ids,
            embeddings=vectors,
            metadatas=[{"text": chunk} for chunk in chunks]
        )

        config = {"db_path": db_path}
        with open("RAG/config.json", "w", encoding="utf-8") as f:
            json.dump(config, f)

        logger.success("Сохранение векторов завершено успешно.")

    except Exception as e:
        logger.exception(f"Ошибка при сохранении чанков с векторами: {e}")


def clear_db(db_path=DB_PATH) -> None:
    """
    Очищает коллекцию документов в базе данных ChromaDB.
    """
    try:
        logger.warning("Очистка базы данных...")
        chroma_client = chromadb.PersistentClient(path=db_path)
        collection = chroma_client.get_or_create_collection(name="documents")
        collection.delete(where={"id": {"$ne": ""}})
        logger.success("База данных очищена.")
    except Exception as e:
        logger.exception(f"Ошибка при очистке базы данных: {e}")


if __name__ == '__main__':
    file_path = r""  # Замените на путь к файлу
    save_chunks_with_vectors(file_path)
