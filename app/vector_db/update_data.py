from vector_db.base_define import WeaviateClientSingleton

def update_data(uuid = "" , className = "Table", dataObject = {"name": "updated"}):
    client = WeaviateClientSingleton("http://weaviate:8080")

    client.data_object.update(
        class_name = className,
        uuid = uuid,
        data_object = dataObject
    )
