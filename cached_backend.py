import requests
import time

class BackendMenuFetcher:
    ttl_seconds = 15 * 60

    def __init__(self, backendBaseUrl):
        self.backendBaseUrl = backendBaseUrl
        self.__fetch_recipe_list()
    
    def __fetch_recipe_list(self):
        self.recipe_json = requests.get(self.backendBaseUrl + 'recipes/').json()
        self.last_fetched = time.time()

    def fetch_recipe_list(self):
        if time.time() > self.last_fetched + BackendMenuFetcher.ttl_seconds:
            self.__fetch_recipe_list()

        return self.recipe_json
