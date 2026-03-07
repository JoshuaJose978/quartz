---
title: Python Collections Module (Real-World Applications and Examples)
---

## Introduction

The `collections` module provides specialized container datatypes that extend Python's built-in containers (dict, list, set, tuple). These are designed to solve common programming problems more efficiently and elegantly.

```python
from collections import Counter, deque, namedtuple, defaultdict, OrderedDict, ChainMap, UserDict
```

---

## 1. Counter: Smart Counting and Frequency Analysis

### What it is:
A dictionary subclass designed for counting hashable objects. Think of it as a mathematical multiset.

### Real-life Use Cases:
- **E-commerce**: Tracking product popularity
- **Analytics**: Counting website visits, user actions
- **Text Processing**: Word frequency analysis
- **Gaming**: Tracking player statistics

### Practical Examples:

#### Example 1: E-commerce Product Analytics
```python
from collections import Counter

# Track which products customers view most
product_views = ['laptop', 'mouse', 'keyboard', 'laptop', 'monitor', 
                'mouse', 'laptop', 'headphones', 'mouse', 'laptop']

view_counter = Counter(product_views)
print(view_counter)
# Counter({'laptop': 4, 'mouse': 3, 'keyboard': 1, 'monitor': 1, 'headphones': 1})

# Find top 2 most viewed products
top_products = view_counter.most_common(2)
print(f"Top products: {top_products}")
# Top products: [('laptop', 4), ('mouse', 3)]

# Add more data (e.g., from another day)
new_views = ['monitor', 'monitor', 'headphones', 'laptop']
view_counter.update(new_views)
print(view_counter)
# Counter({'laptop': 5, 'mouse': 3, 'monitor': 3, 'headphones': 2, 'keyboard': 1})
```

#### Example 2: Text Analysis for Content Strategy
```python
import re
from collections import Counter

def analyze_content_keywords(text):
    # Extract words (simplified)
    words = re.findall(r'\b\w+\b', text.lower())
    # Filter out common words
    stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by'}
    filtered_words = [word for word in words if word not in stop_words and len(word) > 3]
    
    return Counter(filtered_words)

blog_post = """
Python programming language offers many powerful features for data analysis.
Machine learning with Python has become increasingly popular among developers.
Python's simplicity and extensive libraries make programming efficient and enjoyable.
"""

keywords = analyze_content_keywords(blog_post)
print("Top keywords:", keywords.most_common(5))
# Top keywords: [('python', 3), ('programming', 2), ('analysis', 1), ('machine', 1), ('learning', 1)]
```

---

## 2. deque: High-Performance Queues and Stacks

### What it is:
A double-ended queue optimized for fast appends and pops from both ends.

### Real-life Use Cases:
- **Web Servers**: Request queues, rate limiting
- **Gaming**: Recent player actions, undo/redo systems
- **Data Processing**: Sliding window calculations
- **System Monitoring**: Keeping recent logs

### Practical Examples:

#### Example 1: Rate Limiting System
```python
from collections import deque
import time

class RateLimiter:
    def __init__(self, max_requests=5, time_window=60):
        self.max_requests = max_requests
        self.time_window = time_window
        self.requests = deque()
    
    def allow_request(self, user_id):
        now = time.time()
        
        # Remove old requests outside the time window
        while self.requests and self.requests[0][1] < now - self.time_window:
            self.requests.popleft()  # O(1) operation!
        
        # Check if user has exceeded the limit
        user_requests = sum(1 for uid, _ in self.requests if uid == user_id)
        
        if user_requests < self.max_requests:
            self.requests.append((user_id, now))
            return True
        return False

# Usage
limiter = RateLimiter(max_requests=3, time_window=10)

print(limiter.allow_request("user1"))  # True
print(limiter.allow_request("user1"))  # True
print(limiter.allow_request("user1"))  # True
print(limiter.allow_request("user1"))  # False (rate limited)
```

#### Example 2: Sliding Window Analytics
```python
from collections import deque

class SlidingWindowMetrics:
    def __init__(self, window_size=10):
        self.window_size = window_size
        self.values = deque(maxlen=window_size)  # Automatically maintains size
        self.sum = 0
    
    def add_value(self, value):
        if len(self.values) == self.window_size:
            # Remove the oldest value from sum
            self.sum -= self.values[0]  # Will be automatically removed
        
        self.values.append(value)
        self.sum += value
    
    def get_average(self):
        return self.sum / len(self.values) if self.values else 0
    
    def get_recent_values(self, n=3):
        # Get n most recent values
        return list(self.values)[-n:]

# Usage for monitoring server response times
metrics = SlidingWindowMetrics(window_size=5)

response_times = [120, 150, 98, 200, 180, 95, 110, 165]
for time_ms in response_times:
    metrics.add_value(time_ms)
    print(f"Added {time_ms}ms, Average: {metrics.get_average():.1f}ms")

print(f"Recent 3 values: {metrics.get_recent_values(3)}")
```

---

## 3. namedtuple: Self-Documenting Data Structures

### What it is:
Creates tuple subclasses with named fields, making code more readable and self-documenting.

### Real-life Use Cases:
- **APIs**: Structured response objects
- **Database**: Row representations
- **Configuration**: Settings objects
- **Coordinates**: Points, colors, etc.

### Practical Examples:

#### Example 1: API Response Structure
```python
from collections import namedtuple

# Define structures for API responses
User = namedtuple('User', ['id', 'name', 'email', 'role', 'created_at'])
Product = namedtuple('Product', ['id', 'name', 'price', 'category', 'in_stock'])

# Simulate API responses
def get_user(user_id):
    # Instead of returning a plain tuple or dict
    return User(
        id=user_id,
        name="John Doe", 
        email="john@example.com",
        role="admin",
        created_at="2024-01-15"
    )

def get_product(product_id):
    return Product(
        id=product_id,
        name="Wireless Mouse",
        price=29.99,
        category="Electronics",
        in_stock=True
    )

# Usage - much more readable than tuple indices!
user = get_user(123)
product = get_product(456)

print(f"User: {user.name} ({user.email})")  # Instead of user[1], user[2]
print(f"Product: {product.name} - ${product.price}")

# namedtuples are still tuples - immutable and hashable
users_set = {user}  # Can be added to sets
user_id, user_name = user.id, user.name  # Can be unpacked

# Create modified copies
premium_user = user._replace(role="premium")
print(f"Upgraded user: {premium_user}")
```

#### Example 2: Game Development - Coordinates and Colors
```python
from collections import namedtuple

# Game entities
Point = namedtuple('Point', ['x', 'y'])
Color = namedtuple('Color', ['r', 'g', 'b', 'alpha'])
GameObject = namedtuple('GameObject', ['position', 'color', 'size', 'velocity'])

# Create game objects
player_pos = Point(100, 200)
enemy_pos = Point(300, 150)
red_color = Color(255, 0, 0, 1.0)
blue_color = Color(0, 0, 255, 0.8)

player = GameObject(
    position=player_pos,
    color=red_color,
    size=Point(32, 32),
    velocity=Point(5, 0)
)

enemy = GameObject(
    position=enemy_pos,
    color=blue_color,
    size=Point(24, 24),
    velocity=Point(-2, 1)
)

def move_object(obj, time_delta):
    new_x = obj.position.x + obj.velocity.x * time_delta
    new_y = obj.position.y + obj.velocity.y * time_delta
    new_position = Point(new_x, new_y)
    return obj._replace(position=new_position)

# Game loop simulation
for frame in range(3):
    player = move_object(player, 1.0)
    enemy = move_object(enemy, 1.0)
    print(f"Frame {frame}: Player at {player.position}, Enemy at {enemy.position}")
```

---

## 4. defaultdict: Never Worry About KeyError Again

### What it is:
A dictionary subclass that automatically creates missing values using a factory function.

### Real-life Use Cases:
- **Data Grouping**: Grouping items by category
- **Graph Algorithms**: Adjacency lists
- **Caching**: Automatic cache initialization
- **Aggregation**: Collecting values by key

### Practical Examples:

#### Example 1: E-commerce Order Analysis
```python
from collections import defaultdict
import json

# Sample order data
orders = [
    {"customer_id": "C001", "product": "laptop", "quantity": 1, "amount": 999.99},
    {"customer_id": "C002", "product": "mouse", "quantity": 2, "amount": 49.98},
    {"customer_id": "C001", "product": "keyboard", "quantity": 1, "amount": 79.99},
    {"customer_id": "C003", "product": "monitor", "quantity": 1, "amount": 299.99},
    {"customer_id": "C002", "product": "laptop", "quantity": 1, "amount": 999.99},
    {"customer_id": "C001", "product": "mouse", "quantity": 1, "amount": 24.99},
]

# Group orders by customer - no KeyError handling needed!
customer_orders = defaultdict(list)
customer_totals = defaultdict(float)
product_sales = defaultdict(int)

for order in orders:
    customer_id = order["customer_id"]
    
    # Automatically creates empty list if customer not seen before
    customer_orders[customer_id].append(order)
    
    # Automatically starts with 0.0 if customer not seen before
    customer_totals[customer_id] += order["amount"]
    
    # Count product sales
    product_sales[order["product"]] += order["quantity"]

print("Customer Orders:")
for customer, orders_list in customer_orders.items():
    print(f"{customer}: {len(orders_list)} orders, Total: ${customer_totals[customer]:.2f}")

print("\nProduct Sales:")
for product, quantity in product_sales.items():
    print(f"{product}: {quantity} units sold")
```

#### Example 2: Social Network Graph
```python
from collections import defaultdict

class SocialNetwork:
    def __init__(self):
        # Each user has a list of friends - automatically creates empty list
        self.friendships = defaultdict(set)
        # Track mutual interests
        self.interests = defaultdict(set)
    
    def add_friendship(self, user1, user2):
        self.friendships[user1].add(user2)
        self.friendships[user2].add(user1)
    
    def add_interest(self, user, interest):
        self.interests[interest].add(user)
    
    def get_mutual_friends(self, user1, user2):
        return self.friendships[user1] & self.friendships[user2]
    
    def suggest_friends(self, user):
        suggestions = set()
        # Find friends of friends
        for friend in self.friendships[user]:
            for friend_of_friend in self.friendships[friend]:
                if friend_of_friend != user and friend_of_friend not in self.friendships[user]:
                    suggestions.add(friend_of_friend)
        return suggestions
    
    def find_users_with_interest(self, interest):
        return self.interests[interest]  # Returns empty set if interest doesn't exist

# Usage
network = SocialNetwork()

# Add friendships
network.add_friendship("Alice", "Bob")
network.add_friendship("Bob", "Charlie")
network.add_friendship("Alice", "David")
network.add_friendship("Charlie", "Eve")

# Add interests
for user in ["Alice", "Charlie", "Eve"]:
    network.add_interest(user, "Python")

for user in ["Bob", "David"]:
    network.add_interest(user, "JavaScript")

# Analytics
print("Alice's friends:", network.friendships["Alice"])
print("Suggested friends for Alice:", network.suggest_friends("Alice"))
print("Python enthusiasts:", network.find_users_with_interest("Python"))
print("Mutual friends of Alice and Bob:", network.get_mutual_friends("Alice", "Bob"))
```

---

## 5. OrderedDict: When Order Matters

### What it is:
A dictionary that remembers insertion order and provides order-specific operations.

### Real-life Use Cases:
- **Configuration**: Maintaining config file order
- **Caching**: LRU (Least Recently Used) cache
- **Data Processing**: Preserving processing pipeline order
- **APIs**: Maintaining field order in responses

### Practical Examples:

#### Example 1: LRU Cache Implementation
```python
from collections import OrderedDict

class LRUCache:
    def __init__(self, capacity=3):
        self.capacity = capacity
        self.cache = OrderedDict()
    
    def get(self, key):
        if key in self.cache:
            # Move to end (most recently used)
            self.cache.move_to_end(key)
            return self.cache[key]
        return None
    
    def put(self, key, value):
        if key in self.cache:
            # Update existing key
            self.cache[key] = value
            self.cache.move_to_end(key)
        else:
            # Add new key
            if len(self.cache) >= self.capacity:
                # Remove least recently used (first item)
                self.cache.popitem(last=False)
            self.cache[key] = value
    
    def display_cache(self):
        print("Cache (LRU -> MRU):", list(self.cache.items()))

# Usage
cache = LRUCache(capacity=3)

# Add some data
cache.put("user:123", {"name": "Alice", "email": "alice@example.com"})
cache.put("user:456", {"name": "Bob", "email": "bob@example.com"})
cache.put("user:789", {"name": "Charlie", "email": "charlie@example.com"})
cache.display_cache()

# Access user:123 (makes it most recently used)
user = cache.get("user:123")
cache.display_cache()

# Add another user (should evict user:456 as it's LRU)
cache.put("user:999", {"name": "David", "email": "david@example.com"})
cache.display_cache()
```

#### Example 2: Configuration Manager
```python
from collections import OrderedDict
import json

class ConfigManager:
    def __init__(self):
        self.config = OrderedDict()
    
    def load_from_dict(self, config_dict):
        # Preserve the order of configuration sections
        for section, settings in config_dict.items():
            self.config[section] = OrderedDict(settings)
    
    def get_setting(self, section, key, default=None):
        return self.config.get(section, {}).get(key, default)
    
    def set_setting(self, section, key, value):
        if section not in self.config:
            self.config[section] = OrderedDict()
        self.config[section][key] = value
    
    def export_config(self):
        # Maintains order for readability
        return dict(self.config)
    
    def get_sections_in_order(self):
        return list(self.config.keys())

# Usage
config = ConfigManager()

# Load configuration (order matters for readability/organization)
initial_config = OrderedDict([
    ('database', OrderedDict([
        ('host', 'localhost'),
        ('port', 5432),
        ('name', 'myapp'),
        ('ssl', True)
    ])),
    ('api', OrderedDict([
        ('base_url', 'https://api.example.com'),
        ('timeout', 30),
        ('retries', 3)
    ])),
    ('logging', OrderedDict([
        ('level', 'INFO'),
        ('format', '%(asctime)s - %(levelname)s - %(message)s'),
        ('file', 'app.log')
    ]))
])

config.load_from_dict(initial_config)

print("Configuration sections in order:", config.get_sections_in_order())
print("Database host:", config.get_setting('database', 'host'))

# Add new section - will be added at the end
config.set_setting('cache', 'redis_url', 'redis://localhost:6379')
print("Updated sections:", config.get_sections_in_order())
```

---

## 6. ChainMap: Unified View of Multiple Mappings

### What it is:
Creates a single view of multiple dictionaries, searching through them in order.

### Real-life Use Cases:
- **Configuration**: Combining default, user, and environment configs
- **Scoping**: Variable scopes in programming languages
- **Template Systems**: Context inheritance
- **Settings Management**: Layered configuration systems

### Practical Examples:

#### Example 1: Application Configuration System
```python
from collections import ChainMap
import os

class AppConfig:
    def __init__(self, app_name="myapp"):
        # Configuration priority: CLI args > environment > user config > defaults
        self.defaults = {
            'debug': False,
            'host': 'localhost',
            'port': 8000,
            'database_url': 'sqlite:///app.db',
            'log_level': 'INFO'
        }
        
        self.user_config = {}
        self.env_config = {}
        self.cli_args = {}
        
        self._load_env_config(app_name.upper())
        self.config = ChainMap(
            self.cli_args,    # Highest priority
            self.env_config,
            self.user_config,
            self.defaults     # Lowest priority
        )
    
    def _load_env_config(self, prefix):
        """Load configuration from environment variables"""
        env_mapping = {
            f'{prefix}_DEBUG': 'debug',
            f'{prefix}_HOST': 'host',
            f'{prefix}_PORT': 'port',
            f'{prefix}_DATABASE_URL': 'database_url',
            f'{prefix}_LOG_LEVEL': 'log_level'
        }
        
        for env_var, config_key in env_mapping.items():
            if env_var in os.environ:
                value = os.environ[env_var]
                # Simple type conversion
                if config_key in ['debug']:
                    value = value.lower() in ('true', '1', 'yes')
                elif config_key in ['port']:
                    value = int(value)
                self.env_config[config_key] = value
    
    def load_user_config(self, user_settings):
        """Load user-specific configuration"""
        self.user_config.update(user_settings)
        # Rebuild ChainMap to reflect changes
        self.config = ChainMap(self.cli_args, self.env_config, 
                              self.user_config, self.defaults)
    
    def set_cli_arg(self, key, value):
        """Set configuration from command line arguments"""
        self.cli_args[key] = value
        self.config = ChainMap(self.cli_args, self.env_config,
                              self.user_config, self.defaults)
    
    def get(self, key, default=None):
        return self.config.get(key, default)
    
    def show_config_source(self, key):
        """Show which configuration source provides a value"""
        for i, mapping in enumerate(['CLI args', 'Environment', 'User config', 'Defaults']):
            if key in list(self.config.maps)[i]:
                return f"{key} = {self.config[key]} (from {mapping})"
        return f"{key} not found"

# Usage example
# Set some environment variables for demo
os.environ['MYAPP_DEBUG'] = 'true'
os.environ['MYAPP_PORT'] = '9000'

config = AppConfig('myapp')

# Load user configuration
user_settings = {
    'host': '0.0.0.0',
    'database_url': 'postgresql://user:pass@db:5432/prod'
}
config.load_user_config(user_settings)

# Set CLI argument (highest priority)
config.set_cli_arg('port', 3000)

# Show final configuration and sources
print("Final Configuration:")
for key in ['debug', 'host', 'port', 'database_url', 'log_level']:
    print(f"  {config.show_config_source(key)}")

print(f"\nServer will run on {config.get('host')}:{config.get('port')}")
```

#### Example 2: Template Context Inheritance
```python
from collections import ChainMap

class TemplateRenderer:
    def __init__(self):
        # Global context available to all templates
        self.global_context = {
            'site_name': 'My Website',
            'current_year': 2024,
            'version': '1.0.0'
        }
        
    def render_page(self, template_name, page_context=None, user_context=None):
        """Render a page with layered context"""
        if page_context is None:
            page_context = {}
        if user_context is None:
            user_context = {}
        
        # Context priority: page > user > global
        full_context = ChainMap(page_context, user_context, self.global_context)
        
        return self._render_template(template_name, full_context)
    
    def _render_template(self, template_name, context):
        """Simulate template rendering"""
        template_content = {
            'homepage': 'Welcome to {site_name}! User: {username}, Year: {current_year}',
            'profile': 'Hello {username}! Your role: {role}. Version: {version}',
            'admin': 'Admin Panel - {username} ({role}) - Debug: {debug_mode}'
        }
        
        template = template_content.get(template_name, 'Template not found')
        
        # Simple template substitution
        try:
            return template.format(**context)
        except KeyError as e:
            return f"Missing variable {e} in template {template_name}"

# Usage
renderer = TemplateRenderer()

# Different users with different contexts
admin_user_context = {
    'username': 'admin',
    'role': 'administrator',
    'permissions': ['read', 'write', 'delete']
}

regular_user_context = {
    'username': 'john_doe',
    'role': 'user'
}

# Different pages with specific context
homepage_context = {
    'featured_products': ['laptop', 'mouse'],
    'current_year': 2024  # This will override global current_year
}

admin_page_context = {
    'debug_mode': True,
    'active_users': 150
}

# Render different pages for different users
print("Homepage for regular user:")
print(renderer.render_page('homepage', homepage_context, regular_user_context))

print("\nAdmin panel for admin user:")
print(renderer.render_page('admin', admin_page_context, admin_user_context))

print("\nProfile page for regular user:")
print(renderer.render_page('profile', {}, regular_user_context))
```

---

## 7. UserDict, UserList, UserString: Custom Container Base Classes

### What they are:
Wrapper classes that make it easier to create custom containers by subclassing.

### Real-life Use Cases:
- **Domain Objects**: Creating business-specific containers
- **Validation**: Adding validation to standard containers
- **Logging**: Tracking access to data structures
- **Caching**: Adding caching behavior to containers

### Practical Examples:

#### Example 1: Validated Configuration Dictionary
```python
from collections import UserDict
import re
from typing import Any, Dict

class ValidatedConfig(UserDict):
    """A dictionary that validates configuration values"""
    
    # Define validation rules
    VALIDATORS = {
        'email': lambda x: re.match(r'^[^@]+@[^@]+\.[^@]+$', str(x)) is not None,
        'port': lambda x: isinstance(x, int) and 1 <= x <= 65535,
        'url': lambda x: isinstance(x, str) and (x.startswith('http://') or x.startswith('https://')),
        'debug': lambda x: isinstance(x, bool),
        'timeout': lambda x: isinstance(x, (int, float)) and x > 0
    }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.history = []  # Track changes
    
    def __setitem__(self, key: str, value: Any):
        # Validate based on key name patterns
        self._validate_item(key, value)
        
        # Log the change
        old_value = self.data.get(key, '<not set>')
        self.history.append({
            'action': 'set',
            'key': key,
            'old_value': old_value,
            'new_value': value,
            'timestamp': __import__('time').time()
        })
        
        super().__setitem__(key, value)
    
    def _validate_item(self, key: str, value: Any):
        """Validate item based on key patterns"""
        for pattern, validator in self.VALIDATORS.items():
            if pattern in key.lower():
                if not validator(value):
                    raise ValueError(f"Invalid {pattern} value for key '{key}': {value}")
        
        # Additional custom validations
        if key.endswith('_path') and not isinstance(value, str):
            raise ValueError(f"Path keys must be strings: {key}")
    
    def get_validation_history(self):
        """Get history of all changes"""
        return self.history.copy()
    
    def validate_all(self):
        """Validate all current items"""
        errors = []
        for key, value in self.data.items():
            try:
                self._validate_item(key, value)
            except ValueError as e:
                errors.append(str(e))
        return errors

# Usage
config = ValidatedConfig()

# Valid assignments
config['admin_email'] = 'admin@example.com'
config['server_port'] = 8080
config['api_url'] = 'https://api.example.com'
config['debug'] = True
config['connection_timeout'] = 30.0
config['log_path'] = '/var/log/app.log'

print("Configuration:", dict(config))

# This will raise validation errors
try:
    config['invalid_email'] = 'not-an-email'
except ValueError as e:
    print(f"Validation error: {e}")

try:
    config['bad_port'] = 99999
except ValueError as e:
    print(f"Validation error: {e}")

# Check history
print("\nConfiguration changes:")
for change in config.get_validation_history():
    print(f"  {change['key']}: {change['old_value']} -> {change['new_value']}")
```

#### Example 2: Smart List with Statistics
```python
from collections import UserList
import statistics
from typing import Union, List

class StatsList(UserList):
    """A list that automatically calculates statistics"""
    
    def __init__(self, iterable=None):
        super().__init__(iterable or [])
        self._stats_cache = {}
        self._cache_valid = False
    
    def append(self, item: Union[int, float]):
        if not isinstance(item, (int, float)):
            raise TypeError("StatsList only accepts numeric values")
        super().append(item)
        self._invalidate_cache()
    
    def extend(self, iterable):
        # Validate all items first
        for item in iterable:
            if not isinstance(item, (int, float)):
                raise TypeError("StatsList only accepts numeric values")
        super().extend(iterable)
        self._invalidate_cache()
    
    def __setitem__(self, index, value):
        if not isinstance(value, (int, float)):
            raise TypeError("StatsList only accepts numeric values")
        super().__setitem__(index, value)
        self._invalidate_cache()
    
    def _invalidate_cache(self):
        """Mark statistics cache as invalid"""
        self._cache_valid = False
        self._stats_cache.clear()
    
    def _calculate_stats(self):
        """Calculate and cache statistics"""
        if not self.data:
            return {}
        
        self._stats_cache = {
            'mean': statistics.mean(self.data),
            'median': statistics.median(self.data),
            'min': min(self.data),
            'max': max(self.data),
            'sum': sum(self.data),
            'count': len(self.data)
        }
        
        if len(self.data) > 1:
            self._stats_cache['stdev'] = statistics.stdev(self.data)
        else:
            self._stats_cache['stdev'] = 0.0
        
        self._cache_valid = True
    
    def get_stats(self) -> dict:
        """Get comprehensive statistics"""
        if not self._cache_valid:
            self._calculate_stats()
        return self._stats_cache.copy()
    
    def mean(self) -> float:
        stats = self.get_stats()
        return stats.get('mean', 0.0)
    
    def median(self) -> float:
        stats = self.get_stats()
        return stats.get('median', 0.0)
    
    def add_batch(self, values: List[Union[int, float]]):
        """Add multiple values efficiently"""
        # Validate first
        for value in values:
            if not isinstance(value, (int, float)):
                raise TypeError(f"Invalid value type: {type(value)}")
        
        # Add all at once
        self.data.extend(values)
        self._invalidate_cache()
    
    def summary(self) -> str:
        """Get a formatted summary"""
        stats = self.get_stats()
        if not stats:
            return "Empty list - no statistics available"
        
        return f"""
Statistics Summary:
  Count: {stats['count']}
  Sum: {stats['sum']:.2f}
  Mean: {stats['mean']:.2f}
  Median: {stats['median']:.2f}
  Min: {stats['min']:.2f}
  Max: {stats['max']:.2f}
  Std Dev: {stats['stdev']:.2f}
        """.strip()
# Usage
# Stock price tracking
stock_prices = StatsList([100.50, 102.25, 99.75, 101.00, 103.50])

print("Initial prices:", list(stock_prices))
print(f"Average price: ${stock_prices.mean():.2f}")
print(f"Median price: ${stock_prices.median():.2f}")

# Add more prices
stock_prices.add_batch([104.25, 102.75, 101.50, 100.25, 99.50])
print("\nAfter adding more prices:")
print(stock_prices.summary())

# Real-world usage: Server response time monitoring
response_times = StatsList()

# Simulate collecting response times
import random
random.seed(42)  # For reproducible results

for _ in range(20):
    # Simulate response times between 50ms and 200ms
    time_ms = random.uniform(50, 200)
    response_times.append(round(time_ms, 2))

print("\nServer Response Time Analysis:")
print(response_times.summary())

# Alert if average response time is too high
if response_times.mean() > 150:
    print("⚠️  WARNING: Average response time is high!")
else:
    print("✅ Response times are within acceptable range")
```

#### Example 3: Smart String with Text Analysis
```python
from collections import UserString
import re
from typing import Dict, List

class AnalyzableText(UserString):
    """A string that provides text analysis capabilities"""
    
    def __init__(self, seq=""):
        super().__init__(seq)
        self._analysis_cache = {}
        self._cache_valid = False
    
    def __add__(self, other):
        """Override addition to return AnalyzableText"""
        result = super().__add__(other)
        return AnalyzableText(result.data)
    
    def __setattr__(self, name, value):
        super().__setattr__(name, value)
        if name == 'data':
            self._invalidate_cache()
    
    def _invalidate_cache(self):
        """Mark analysis cache as invalid"""
        if hasattr(self, '_cache_valid'):
            self._cache_valid = False
            self._analysis_cache.clear()
    
    def _analyze(self):
        """Perform comprehensive text analysis"""
        text = self.data.lower()
        
        # Word analysis
        words = re.findall(r'\b\w+\b', text)
        sentences = re.split(r'[.!?]+', self.data)
        sentences = [s.strip() for s in sentences if s.strip()]
        
        # Character analysis
        chars_no_space = re.sub(r'\s', '', self.data)
        
        self._analysis_cache = {
            'word_count': len(words),
            'sentence_count': len(sentences),
            'character_count': len(self.data),
            'character_count_no_spaces': len(chars_no_space),
            'average_words_per_sentence': len(words) / max(len(sentences), 1),
            'unique_words': len(set(words)),
            'most_common_words': self._get_word_frequency(words)[:5],
            'readability_score': self._calculate_readability(words, sentences)
        }
        
        self._cache_valid = True
    
    def _get_word_frequency(self, words: List[str]) -> List[tuple]:
        """Get word frequency sorted by count"""
        from collections import Counter
        # Filter out common stop words
        stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'is', 'are', 'was', 'were'}
        filtered_words = [w for w in words if w not in stop_words and len(w) > 2]
        return Counter(filtered_words).most_common()
    
    def _calculate_readability(self, words: List[str], sentences: List[str]) -> float:
        """Simple readability score (Flesch Reading Ease approximation)"""
        if not sentences or not words:
            return 0.0
        
        avg_sentence_length = len(words) / len(sentences)
        # Simplified syllable count (approximate)
        syllable_count = sum(max(1, len(re.findall(r'[aeiouy]', word.lower()))) for word in words)
        avg_syllables_per_word = syllable_count / len(words) if words else 0
        
        # Simplified Flesch Reading Ease
        score = 206.835 - (1.015 * avg_sentence_length) - (84.6 * avg_syllables_per_word)
        return max(0, min(100, score))  # Clamp between 0-100
    
    def get_analysis(self) -> Dict:
        """Get comprehensive text analysis"""
        if not self._cache_valid:
            self._analyze()
        return self._analysis_cache.copy()
    
    def word_count(self) -> int:
        """Get word count"""
        return self.get_analysis()['word_count']
    
    def readability(self) -> float:
        """Get readability score (0-100, higher is more readable)"""
        return self.get_analysis()['readability_score']
    
    def summary(self) -> str:
        """Get formatted analysis summary"""
        analysis = self.get_analysis()
        
        readability_level = "Very Easy" if analysis['readability_score'] >= 90 else \
                           "Easy" if analysis['readability_score'] >= 80 else \
                           "Fairly Easy" if analysis['readability_score'] >= 70 else \
                           "Standard" if analysis['readability_score'] >= 60 else \
                           "Fairly Difficult" if analysis['readability_score'] >= 50 else \
                           "Difficult"
        
        return f"""
Text Analysis Summary:
  Words: {analysis['word_count']}
  Sentences: {analysis['sentence_count']}
  Characters: {analysis['character_count']} ({analysis['character_count_no_spaces']} without spaces)
  Unique words: {analysis['unique_words']}
  Avg words per sentence: {analysis['average_words_per_sentence']:.1f}
  Readability: {analysis['readability_score']:.1f}/100 ({readability_level})
  
Top words: {', '.join([f"{word}({count})" for word, count in analysis['most_common_words']])}
        """.strip()
    
    def extract_emails(self) -> List[str]:
        """Extract email addresses from text"""
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        return re.findall(email_pattern, self.data)
    
    def extract_urls(self) -> List[str]:
        """Extract URLs from text"""
        url_pattern = r'https?://[^\s<>"{}|\\^`[\]]+'
        return re.findall(url_pattern, self.data)

# Usage examples
# Blog post analysis
blog_content = AnalyzableText("""
Welcome to our comprehensive guide on Python programming! 
Python is a powerful, versatile programming language that has gained tremendous popularity 
in recent years. Whether you're a beginner just starting out or an experienced developer 
looking to expand your skills, Python offers something for everyone.

In this article, we'll explore the fundamental concepts of Python programming, 
including variables, functions, and object-oriented programming principles. 
We'll also dive into practical applications and real-world examples that demonstrate 
Python's capabilities in web development, data analysis, and automation.

For more information, visit our website at https://pythonguide.com or contact us 
at support@pythonguide.com. You can also reach our technical team at tech@pythonguide.com.
""")

print("Blog Post Analysis:")
print(blog_content.summary())

# Extract contact information
emails = blog_content.extract_emails()
urls = blog_content.extract_urls()
print(f"\nContact Info Found:")
print(f"  Emails: {emails}")
print(f"  URLs: {urls}")

# Social media post analysis
tweet = AnalyzableText("Just discovered an amazing Python library! 🐍 Check it out: https://github.com/example/awesome-lib #Python #Programming")

print(f"\nTweet Analysis:")
print(f"  Character count: {len(tweet)} (Twitter limit: 280)")
print(f"  Word count: {tweet.word_count()}")
print(f"  URLs found: {tweet.extract_urls()}")
print(f"  Readability: {tweet.readability():.1f}/100")

# String operations still work
enhanced_tweet = tweet + " Really impressed with the documentation!"
print(f"\nEnhanced tweet word count: {enhanced_tweet.word_count()}")
```

---

## Comprehensive Real-World Integration Example

Let's combine multiple `collections` types in a realistic application - an **E-commerce Analytics Dashboard**:

```python
from collections import Counter, deque, namedtuple, defaultdict, OrderedDict, ChainMap
import time
import random
from datetime import datetime, timedelta

# Data structures
Order = namedtuple('Order', ['id', 'customer_id', 'product_id', 'quantity', 'amount', 'timestamp'])
Customer = namedtuple('Customer', ['id', 'name', 'email', 'tier'])

class EcommerceAnalytics:
    def __init__(self, max_recent_orders=1000):
        # Counter: Track product popularity and customer order frequency
        self.product_sales = Counter()
        self.customer_order_count = Counter()
        
        # deque: Keep recent orders for real-time analytics
        self.recent_orders = deque(maxlen=max_recent_orders)
        
        # defaultdict: Group data efficiently
        self.orders_by_customer = defaultdict(list)
        self.revenue_by_day = defaultdict(float)
        self.orders_by_product = defaultdict(list)
        
        # OrderedDict: Maintain time-series data
        self.hourly_sales = OrderedDict()
        
        # ChainMap: Configuration management
        self.config = ChainMap(
            {},  # Runtime config (highest priority)
            {'discount_threshold': 1000, 'vip_tier': 'gold'},  # User config
            {'currency': 'USD', 'tax_rate': 0.08}  # Default config
        )
        
        # Store customer info
        self.customers = {}
    
    def add_customer(self, customer: Customer):
        """Add customer information"""
        self.customers[customer.id] = customer
    
    def process_order(self, order: Order):
        """Process a new order through all analytics"""
        # Add to recent orders (deque automatically maintains size)
        self.recent_orders.append(order)
        
        # Update counters
        self.product_sales[order.product_id] += order.quantity
        self.customer_order_count[order.customer_id] += 1
        
        # Update grouped data (defaultdict creates lists automatically)
        self.orders_by_customer[order.customer_id].append(order)
        self.orders_by_product[order.product_id].append(order)
        
        # Update daily revenue
        order_date = datetime.fromtimestamp(order.timestamp).strftime('%Y-%m-%d')
        self.revenue_by_day[order_date] += order.amount
        
        # Update hourly sales (OrderedDict maintains time order)
        hour_key = datetime.fromtimestamp(order.timestamp).strftime('%Y-%m-%d %H:00')
        if hour_key not in self.hourly_sales:
            self.hourly_sales[hour_key] = {'orders': 0, 'revenue': 0.0}
        self.hourly_sales[hour_key]['orders'] += 1
        self.hourly_sales[hour_key]['revenue'] += order.amount
    
    def get_top_products(self, n=5):
        """Get top-selling products"""
        return self.product_sales.most_common(n)
    
    def get_top_customers(self, n=5):
        """Get customers with most orders"""
        top_customer_ids = [cid for cid, count in self.customer_order_count.most_common(n)]
        return [(cid, self.customers.get(cid), count) 
                for cid, count in self.customer_order_count.most_common(n)]
    
    def get_recent_activity(self, minutes=60):
        """Get recent orders within specified minutes"""
        cutoff_time = time.time() - (minutes * 60)
        return [order for order in self.recent_orders if order.timestamp > cutoff_time]
    
    def get_customer_analytics(self, customer_id):
        """Get detailed analytics for a specific customer"""
        orders = self.orders_by_customer[customer_id]
        if not orders:
            return None
        
        total_spent = sum(order.amount for order in orders)
        avg_order_value = total_spent / len(orders)
        
        # Product preferences
        product_quantities = Counter()
        for order in orders:
            product_quantities[order.product_id] += order.quantity
        
        return {
            'customer_id': customer_id,
            'customer_info': self.customers.get(customer_id),
            'total_orders': len(orders),
            'total_spent': total_spent,
            'average_order_value': avg_order_value,
            'favorite_products': product_quantities.most_common(3),
            'first_order': min(orders, key=lambda x: x.timestamp),
            'last_order': max(orders, key=lambda x: x.timestamp)
        }
    
    def get_sales_trend(self, hours=24):
        """Get hourly sales trend"""
        # Get last N hours from OrderedDict
        recent_hours = list(self.hourly_sales.items())[-hours:]
        return recent_hours
    
    def update_config(self, **kwargs):
        """Update runtime configuration"""
        self.config.maps[0].update(kwargs)
    
    def generate_dashboard_report(self):
        """Generate comprehensive dashboard report"""
        recent_activity = self.get_recent_activity(60)  # Last hour
        
        report = f"""
=== E-COMMERCE ANALYTICS DASHBOARD ===
Generated at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

📊 RECENT ACTIVITY (Last Hour):
  Orders: {len(recent_activity)}
  Revenue: ${sum(order.amount for order in recent_activity):.2f}

🏆 TOP PRODUCTS:
"""
        for product_id, quantity in self.get_top_products(5):
            revenue = sum(order.amount for order in self.orders_by_product[product_id])
            report += f"  {product_id}: {quantity} units sold, ${revenue:.2f} revenue\n"
        
        report += "\n👥 TOP CUSTOMERS:\n"
        for customer_id, customer_info, order_count in self.get_top_customers(3):
            name = customer_info.name if customer_info else "Unknown"
            total_spent = sum(order.amount for order in self.orders_by_customer[customer_id])
            report += f"  {name} ({customer_id}): {order_count} orders, ${total_spent:.2f} spent\n"
        
        report += f"\n⚙️  CONFIGURATION:\n"
        report += f"  Currency: {self.config['currency']}\n"
        report += f"  Tax Rate: {self.config['tax_rate']*100}%\n"
        report += f"  Discount Threshold: ${self.config['discount_threshold']}\n"
        
        return report

# Demo usage
def demo_ecommerce_analytics():
    analytics = EcommerceAnalytics()
    
    # Add sample customers
    customers = [
        Customer('C001', 'Alice Johnson', 'alice@example.com', 'gold'),
        Customer('C002', 'Bob Smith', 'bob@example.com', 'silver'),
        Customer('C003', 'Charlie Brown', 'charlie@example.com', 'bronze'),
        Customer('C004', 'Diana Prince', 'diana@example.com', 'gold'),
    ]
    
    for customer in customers:
        analytics.add_customer(customer)
    
    # Generate sample orders
    products = ['laptop', 'mouse', 'keyboard', 'monitor', 'headphones']
    
    base_time = time.time() - (24 * 60 * 60)  # 24 hours ago
    
    for i in range(100):
        order = Order(
            id=f'ORD{i+1:03d}',
            customer_id=random.choice([c.id for c in customers]),
            product_id=random.choice(products),
            quantity=random.randint(1, 3),
            amount=round(random.uniform(10, 500), 2),
            timestamp=base_time + random.uniform(0, 24*60*60)
        )
        analytics.process_order(order)
    
    # Update configuration
    analytics.update_config(discount_threshold=750, special_promotion=True)
    
    # Generate report
    print(analytics.generate_dashboard_report())
    
    # Detailed customer analysis
    print("\n=== DETAILED CUSTOMER ANALYSIS ===")
    customer_analysis = analytics.get_customer_analytics('C001')
    if customer_analysis:
        print(f"Customer: {customer_analysis['customer_info'].name}")
        print(f"Total Orders: {customer_analysis['total_orders']}")
        print(f"Total Spent: ${customer_analysis['total_spent']:.2f}")
        print(f"Average Order: ${customer_analysis['average_order_value']:.2f}")
        print(f"Favorite Products: {customer_analysis['favorite_products']}")

# Run the demo
if __name__ == "__main__":
    demo_ecommerce_analytics()
```

---

## Key Takeaways and Best Practices

### 1. **Choose the Right Tool for the Job**
- **Counter**: When you need to count things or analyze frequencies
- **deque**: When you need efficient queue/stack operations
- **namedtuple**: When you want readable, immutable data structures
- **defaultdict**: When you're grouping or accumulating data
- **OrderedDict**: When order matters beyond just insertion order
- **ChainMap**: When you need layered configuration or scoping
- **User classes**: When you need custom behavior on standard containers

### 2. **Performance Considerations**
- `deque` operations are O(1) at both ends vs O(n) for lists
- `Counter` operations are optimized for counting scenarios
- `defaultdict` eliminates KeyError handling overhead
- User classes add slight overhead but provide flexibility

### 3. **Common Patterns**
- **Data Aggregation**: Use `defaultdict` with `list` or `Counter`
- **Configuration Management**: Use `ChainMap` for layered configs
- **Real-time Analytics**: Use `deque` with `maxlen` for sliding windows
- **Data Validation**: Subclass User classes for custom validation

### 4. **Integration with Other Libraries**
These collections work seamlessly with:
- **Pandas**: For data analysis workflows
- **JSON**: Most are JSON-serializable with minor conversion
- **Multiprocessing**: Thread-safe operations where noted
- **Type Hints**: All support proper type annotations

The `collections` module transforms how you handle data in Python, making code more efficient, readable, and maintainable. Master these tools, and you'll find yourself writing more elegant and powerful Python applications.
