import spacy
from sentence_transformers import SentenceTransformer
import weaviate

client = weaviate.Client("http://weaviate:8080")
schema = {
    "classes": [
        {
            "class": "Sentence",
            "description": "A class to store sentences and their embeddings",
            "properties": [
                {
                    "name": "text",
                    "dataType": ["text"],
                    "description": "The original sentence text",
                },
                {
                    "name": "embedding",
                    "dataType": ["vector"],
                    "description": "The SBERT embedding of the sentence",
                },
            ],
        },
    ],
}

nlp = spacy.load("en_core_web_md")
sentence = "List suppliers who supply red parts?"
doc = nlp(sentence)

# 初始化SBERT模型
model = SentenceTransformer('all-MiniLM-L6-v2')
segSen=[]
for token in doc:
    segSen.append(token.text)

    embedding = model.encode(token.text)
    data_object = {
        "text": token.text,
        "embedding": {"vector": embedding.tolist()},
    }
    vcid = client.data_object.create(data_object, "Sentence")
    print(f"Created Sentence with UUID: {vcid}")
