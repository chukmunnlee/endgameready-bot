import math

class LRU:

   cache_keys = []
   cache = {}
   capacity = 50
   evict = 5

   def normalize_key(self, k):
      return k.strip().replace(' ', '').lower()

   def __init__(self, capacity=50):
      self.capacity = capacity
      self.evict = math.floor(capacity * .1) + 1

   def put(self, key, value):
      norm_key = self.normalize_key(key)
      if len(self.cache_keys) >= self.capacity:
         for _ in range(self.evict):
            k = self.cache_keys.pop(0)
            del self.cache[k]
      self.cache_keys.append(norm_key)
      self.cache[norm_key] = value

   def get(self, key):
      norm_key = self.normalize_key(key)
      if norm_key not in self.cache:
         return False, None
      self.cache_keys.pop(self.cache_keys.index(norm_key))
      self.cache_keys.append(norm_key)
      return True, self.cache[norm_key]

   def keys(self):
      return self.cache_keys
