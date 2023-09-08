import time

class CachedBackendCall:
    ttl_seconds = 15 * 60

    def __init__(self, fetch_function):
        self.fetch_function = fetch_function
        self.__fetch_data()
    
    def __fetch_data(self):
        self.__data = self.fetch_function()
        self.__last_fetched = time.time()

    def fetch_data(self):
        if time.time() > self.__last_fetched + CachedBackendCall.ttl_seconds:
            self.__fetch_data()

        return self.__data
