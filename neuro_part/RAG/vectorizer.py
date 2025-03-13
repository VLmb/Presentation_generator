from chunk_creater import split_text_by_sentences
import json
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.decomposition import TruncatedSVD

def vectorize_chunks(chunks, n_components=10):
    vectorizer = TfidfVectorizer(max_features=400)
    vectors = vectorizer.fit_transform(chunks)

    svd = TruncatedSVD(n_components=n_components)
    reduced_vectors = svd.fit_transform(vectors)

    return reduced_vectors.tolist()


def save_chunks_with_vectors(file_path, output_json="chunks_with_vectors.json"):
    chunks = split_text_by_sentences(file_path)
    vectors = vectorize_chunks(chunks)
    data = [{"chunk": chunk, "vector": vector} for chunk, vector in zip(chunks, vectors)]

    with open(output_json, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

    print(f"JSON файл сохранен: {output_json}")

file_path = r"C:\Users\bm535\Downloads\ОРГ тех.pdf"  # Замените на путь к файлу
save_chunks_with_vectors(file_path)