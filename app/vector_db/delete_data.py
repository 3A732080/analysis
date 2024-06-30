from vector_db.base_define import WeaviateClientSingleton

def delete_data(uuid = "" , className = "Table"):
    client = WeaviateClientSingleton("http://weaviate:8080")

    client.data_object.delete(
        class_name = className,
        uuid = uuid
    )
