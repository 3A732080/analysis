from vector_db.base_define import WeaviateClientSingleton
from helper.base_define import dump

def insert_data(data: dict):
    client = WeaviateClientSingleton("http://weaviate:8080")

    for table, content in data.items():
        dump(f"Table: {table}")

        uuid = client.data_object.create(
            class_name="Table",
            data_object={
                "name": table,
                "ref": {
                    "tag": ["subject", "object", "verb"],
                    "shape": content['attributes']['shape'],
                    "search_default_column": content['attributes']['search_default_column']
                },
            }
        )

        dump(f"Created Table with UUID: {uuid}")

        for column in content["column"]:
            dump(f"Column: {column}")

            uuid = client.data_object.create(
                class_name="Column",
                data_object={
                    "name": column,
                    "ref": {
                        "tag": ["modifier"],
                        "table": table,
                    },
                }
            )

            dump(f"Created Column with UUID: {uuid}")

        for value_list in content["values"]:
            for index, value in enumerate(value_list):
                dump(f"Value: {value}")

                uuid = client.data_object.create(
                    class_name="Value",
                    data_object={
                        "name": value,
                        "ref": {
                            "tag": ["modifier"],
                            "table": table,
                            "table_shape": content['attributes']['shape'],
                            "column": content["column"][index],
                        }
                    }
                )

                dump(f"Created Value with UUID: {uuid}")

    dump('[insert_data] success:true')
