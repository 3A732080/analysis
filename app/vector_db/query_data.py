from vector_db.base_define import WeaviateClientSingleton
from helper.base_define import data_get

def semantic_search(target, select, search):
    client = WeaviateClientSingleton("http://weaviate:8080")

    query_result = client.query.get(
        class_name = target,
        properties = select
    ).with_near_text({
        "concepts": search,
        "boost": 2,  
        "certainty": 0.65
    }).with_additional([
        "id",
        "distance"
    ]).with_limit(5).do()

    return query_result

def is_empty_result(response, keyName):
    res = data_get(response, "data.Get."+ keyName, [])
    return isinstance(res, list) and len(res) == 0