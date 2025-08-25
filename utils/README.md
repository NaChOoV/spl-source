# Utils Module

This module provides reusable utilities for the SPL Source application.

## Singleton Pattern

### Option 1: Inheritance (Recommended for complex classes)

```python
from utils.singleton import Singleton

class MyService(Singleton):
    def __init__(self):
        # Prevent re-initialization
        if hasattr(self, '_initialized') and self._initialized:
            return
            
        # Your initialization code here
        self.data = {}
        self._initialized = True
    
    def do_something(self):
        return "Hello from singleton!"

# Usage
service1 = MyService()
service2 = MyService()
print(service1 is service2)  # True - same instance
```

### Option 2: Decorator (Recommended for simple classes)

```python
from utils.decorators import singleton

@singleton
class MyCache:
    def __init__(self):
        self.cache = {}
    
    def get(self, key):
        return self.cache.get(key)
    
    def set(self, key, value):
        self.cache[key] = value

# Usage
cache1 = MyCache()
cache2 = MyCache()
print(cache1 is cache2)  # True - same instance
```

## When to Use Singletons

✅ **Good candidates:**
- Configuration classes
- Database connection managers
- Cache managers
- Logger services
- External API clients (expensive to create)

❌ **Avoid for:**
- Stateless services
- Controllers
- Simple data classes
- Anything that doesn't need shared state

## Examples

See `examples/singleton_examples.py` for complete working examples.
