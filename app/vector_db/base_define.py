import weaviate


class WeaviateClientSingleton:
    _instance = None

    def __new__(cls, *args, **kwargs): 
        if not cls._instance:
            cls._instance = super(WeaviateClientSingleton, cls).__new__(cls)
            cls._instance.client = weaviate.Client(*args, **kwargs)
            
            if cls._instance.client.is_ready():
                print("成功連接到 Weaviate!")
            else:
                print("連接到 Weaviate 失敗。")

        return cls._instance

    def __getattr__(self, name):
        return getattr(self._instance.client, name)

    def __setattr__(self, name, value):
        if name == "client":
            return super(WeaviateClientSingleton, self).__setattr__(name, value)
        
        return setattr(self._instance.client, name, value)