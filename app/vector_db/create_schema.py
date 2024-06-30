from helper.base_define import dd
from vector_db.base_define import WeaviateClientSingleton

def create_schema():
    client = WeaviateClientSingleton("http://weaviate:8080")

    table = {
        "class": "Table",
        "properties": [
            {
                "name": "name",
                "dataType": ["text"],
            },
            {
                "name": "ref",
                "dataType": ["object"],
                "nestedProperties": [
                    {"dataType": ["text[]"], "name": "tag"},
                    {"dataType": ["text"], "name": "shape"},
                    {"dataType": ["text"], "name": "search_default_column"},
                ],
            },
        ],
        "vectorizer": "text2vec-transformers",
        "vectorIndexConfig": {
            "distance": "cosine",
        },
        "moduleConfig": {
            "text2vec-transformers": {
                "model": "all-MiniLM-L6-v2"
            }
        }
    }

    column = {
        "class": "Column",
        "properties": [
            {
                "name": "name",
                "dataType": ["text"],
            },
            {
                "name": "ref",
                "dataType": ["object"],
                "nestedProperties": [
                    {"dataType": ["text[]"], "name": "tag"},
                    {"dataType": ["text"], "name": "table"},
                ],
            }
        ],
        "vectorizer": "text2vec-transformers",
        "vectorIndexConfig": {
            "distance": "cosine",
        },
        "moduleConfig": {
            "text2vec-transformers": {
                "model": "all-MiniLM-L6-v2"
            }
        }
    }

    value = {
        "class": "Value",
        "properties": [
            {
                "name": "name",
                "dataType": ["text"],
            },
            {
                "name": "ref",
                "dataType": ["object"],
                "nestedProperties": [
                    {"dataType": ["text[]"], "name": "tag"},
                    {"dataType": ["text"], "name": "table"},
                    {"dataType": ["text"], "name": "table_shape"},
                    {"dataType": ["text"], "name": "column"},
                ],
            },
        ],
        "vectorizer": "text2vec-transformers",
        "vectorIndexConfig": {
            "distance": "cosine",
        },
        "moduleConfig": {
            "text2vec-transformers": {
                "model": "all-MiniLM-L6-v2"
            }
        }
    }
  
    client.schema.delete_all()
  
    try:
        client.schema.create_class(table)
        client.schema.create_class(column)
        client.schema.create_class(value)
    except Exception as e:
        dd(f"[create_schema] error: {e}")