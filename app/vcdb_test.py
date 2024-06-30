import weaviate
import json

client = weaviate.Client("http://localhost:8097")

query = """
{
  Get {
    Sentence {
      text
      embedding {
        vector
      }
    }
  }
}
"""

result = client.query.raw(query)
print(json.dumps(result, indent=2))
