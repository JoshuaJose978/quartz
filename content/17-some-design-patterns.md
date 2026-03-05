---
title: Comprehensive Lesson on some Design Patterns
---


## Introduction to Design Patterns

Design patterns are reusable solutions to common software design problems. They represent best practices that have evolved over time as developers have faced and solved similar problems repeatedly. Design patterns help create more maintainable, flexible, and understandable code by following established principles of object-oriented design.

Your code examples demonstrate several important design patterns. Let's explore these patterns in detail.

## 1. Observer Pattern

### Definition
The Observer pattern defines a one-to-many dependency between objects where when one object (the subject) changes state, all its dependents (observers) are notified and updated automatically.

### Code Examples

#### Functional Implementation:
```python
from typing import Callable

def update_observer1(value: str) -> None:
    print(f"Observer 1 received {value}")

def update_observer2(value: str) -> None:
    print(f"Observer 2 received {value}")

UpdateFn = Callable[[str], None]

def notify(update_fns: list[UpdateFn], value: str):
    for update_fn in update_fns:
        update_fn(value)

def main() -> None:
    update_fns = [update_observer1, update_observer2]
    notify(update_fns, "Some data")
```

#### Object-Oriented Implementation:
```python
from abc import ABC, abstractmethod
from dataclasses import dataclass, field

class Observer(ABC):
    @abstractmethod
    def update(self, value: str) -> None:
        pass

@dataclass
class ConcreteObserver(Observer):
    name: str

    def update(self, value: str) -> None:
        print(f"{self.name} received {value}")

@dataclass
class Subject:
    observers: list[Observer] = field(default_factory=list)

    def attach(self, observer: Observer):
        self.observers.append(observer)

    def detach(self, observer: Observer):
        self.observers.remove(observer)

    def notify(self, value: str):
        for observer in self.observers:
            observer.update(value)
```

### Real-World Use Cases

1. **Event Handling Systems**: UI frameworks use observer patterns to handle events (button clicks, mouse movements).
   ```python
   # Simplified UI framework example
   button.add_click_listener(on_button_click)
   ```

2. **Publish-Subscribe Systems**: Message brokers like RabbitMQ or Kafka use this pattern.
   ```python
   # Simplified message broker
   message_broker.subscribe("topic", handle_message)
   ```

3. **Model-View-Controller (MVC)**: The view observes changes in the model.
   ```python
   # MVC example
   model.add_observer(view)
   model.update_data()  # View gets notified
   ```

4. **Data Binding**: Modern frameworks like React, Vue, and Angular use observer pattern for data binding.

### Problems Solved

1. **Decoupling**: The subject doesn't need to know anything about the concrete observers, only that they implement an interface.
2. **Dynamic Relationships**: Observers can be added or removed at runtime.
3. **Broadcast Communication**: Changes can be communicated to multiple objects simultaneously.
4. **Separation of Concerns**: The subject is responsible for maintaining state, observers for reacting to state changes.

## 2. Strategy Pattern

### Definition
The Strategy pattern defines a family of algorithms, encapsulates each one, and makes them interchangeable. It lets the algorithm vary independently from clients that use it.

### Code Examples

#### Functional Implementation:
```python
import random
from typing import Callable

def bubble_sort(data: list[int]) -> list[int]:
    # Implementation...
    return data

def quick_sort(data: list[int]) -> list[int]:
    # Implementation...
    return data

SortFn = Callable[[list[int]], list[int]]

def context(strategy: SortFn, data: list[int]) -> list[int]:
    # Pre-processing logic
    data = [item * 2 for item in data]
    data = [item + random.randint(-10, 10) for item in data]
    
    # Apply strategy
    return strategy(data)
```

#### Object-Oriented Implementation:
```python
from abc import ABC, abstractmethod
import random

class SortStrategy(ABC):
    @abstractmethod
    def sort(self, data: list[int]) -> list[int]:
        pass

class BubbleSortStrategy(SortStrategy):
    def sort(self, data: list[int]) -> list[int]:
        # Implementation...
        return data

class QuickSortStrategy(SortStrategy):
    def sort(self, data: list[int]) -> list[int]:
        # Implementation...
        return data

class Context:
    def __init__(self, strategy: SortStrategy):
        self._strategy = strategy

    def set_strategy(self, strategy: SortStrategy):
        self._strategy = strategy

    def execute(self, data: list[int]) -> list[int]:
        # Pre-processing logic
        data = [item * 2 for item in data]
        data = [item + random.randint(-10, 10) for item in data]
        
        # Apply strategy
        return self._strategy.sort(data)
```

### Real-World Use Cases

1. **Payment Processing**: Different payment methods (credit card, PayPal, cryptocurrency) can be implemented as strategies.
   ```python
   payment_processor = PaymentProcessor(CreditCardStrategy())
   payment_processor.process_payment(100.00)
   
   # Later, switch strategy
   payment_processor.set_strategy(PayPalStrategy())
   payment_processor.process_payment(50.00)
   ```

2. **Compression Algorithms**: Choose between different compression algorithms based on file type.
   ```python
   compressor = Compressor(ZipStrategy())  # For small files
   compressor.compress(small_file)
   
   compressor.set_strategy(RarStrategy())  # For larger files
   compressor.compress(large_file)
   ```

3. **Route Finding**: Navigation apps use different route-finding algorithms (shortest, fastest, most scenic).
   ```python
   navigator = Navigator(ShortestRouteStrategy())
   navigator.find_route(start, end)
   ```

4. **Authentication Methods**: Support different authentication strategies (password, OAuth, SSO).

### Problems Solved

1. **Encapsulation of Algorithms**: Each algorithm is isolated and can be maintained separately.
2. **Runtime Flexibility**: Algorithms can be swapped at runtime.
3. **Elimination of Conditional Logic**: Replaces complex conditionals with strategy objects.
4. **Open/Closed Principle**: New strategies can be added without modifying existing code.

## 3. Template Method Pattern

### Definition
The Template Method pattern defines the skeleton of an algorithm, deferring some steps to subclasses. It lets subclasses redefine certain steps of an algorithm without changing the algorithm's structure.

### Code Examples

#### Functional Implementation:
```python
from typing import Callable

def base_operation1() -> None:
    print("Base operation1")

def base_operation2() -> None:
    print("Base operation2")

def base_operation3() -> None:
    print("Base operation3")

def template_method(
    required_operations1: Callable[[], None],
    required_operations2: Callable[[], None],
    hook1: Callable[[], bool] = lambda: True,
    hook2: Callable[[], None] = lambda: None,
) -> None:
    base_operation1()
    required_operations1()
    base_operation2()
    if hook1():
        base_operation3()
    hook2()
    required_operations2()
```

#### Object-Oriented Implementation:
```python
from abc import ABC, abstractmethod

class Template(ABC):
    def template_method(self) -> None:
        self.base_operation1()
        self.required_operations1()
        self.base_operation2()
        if self.hook1():
            self.base_operation3()
        self.hook2()
        self.required_operations2()

    # Base operations with implementations
    def base_operation1(self) -> None:
        print("Base operation1")

    def base_operation2(self) -> None:
        print("Base operation2")

    def base_operation3(self) -> None:
        print("Base operation3")

    # Abstract operations that must be implemented by subclasses
    @abstractmethod
    def required_operations1(self) -> None:
        pass

    @abstractmethod
    def required_operations2(self) -> None:
        pass

    # Hooks with default implementations
    def hook1(self) -> bool:
        return True

    def hook2(self) -> None:
        pass
```

### Real-World Use Cases

1. **Data Processing Pipelines**: Define the overall process but allow customization of specific steps.
   ```python
   class DataProcessor(Template):
       def required_operations1(self):
           self.extract_data()
           
       def required_operations2(self):
           self.save_results()
           
       # Custom method
       def extract_data(self):
           # Implementation...
   ```

2. **Web Framework Request Handling**:
   ```python
   class RequestHandler(Template):
       def template_method(self, request):
           self.authenticate(request)  # Base operation
           response = self.process_request(request)  # Abstract
           self.log_request(request)  # Base operation
           return self.format_response(response)  # Abstract
   ```

3. **Document Generation**: Define the structure of the document but allow customization of content.
   ```python
   class ReportGenerator(Template):
       def required_operations1(self):
           self.generate_content()
           
       def required_operations2(self):
           self.format_document()
   ```

4. **Build/Deployment Processes**: Define the overall build process with customizable steps.

### Problems Solved

1. **Code Reuse**: Common parts of an algorithm are implemented once in the base class.
2. **Controlled Extension**: Subclasses can only override specific parts of the algorithm.
3. **Inversion of Control**: The template method calls subclass methods, not the other way around.
4. **Standardization**: Ensures all implementations follow the same process structure.

## Design Patterns Implementation Styles

### Functional vs. Object-Oriented Approaches

As demonstrated in the code examples, design patterns can be implemented using both functional and object-oriented approaches:

#### Functional Approach:
- **Advantages**:
  - Often more concise and direct
  - Easier to compose and combine
  - Less boilerplate code
  - Can leverage Python's first-class functions
- **Disadvantages**:
  - May be less explicit about intent
  - Can be harder to enforce contracts
  - May not clearly communicate the design pattern being used

#### Object-Oriented Approach:
- **Advantages**:
  - More explicit structure
  - Clearer contracts through interfaces and abstract classes
  - More familiar representation of classical design patterns
  - Better encapsulation of related functionality
- **Disadvantages**:
  - More verbose
  - Can feel over-engineered for simple cases
  - May introduce unnecessary complexity

### Choosing the Right Approach

The approach you choose should depend on:

1. **Project Size**: Larger projects often benefit from more explicit OO patterns.
2. **Team Familiarity**: Use the approach your team understands best.
3. **Language Idioms**: Python supports both paradigms well.
4. **Complexity**: Simpler problems might be best solved functionally, while complex ones might benefit from OO structure.

## Best Practices and Common Pitfalls

### Best Practices

1. **Understand the Problem Before Applying Patterns**:
   - Don't force patterns where they're not needed
   - Start simple and refactor toward patterns when justified

2. **Maintain Clarity**:
   - Document your pattern usage
   - Use naming conventions that clearly communicate intent

3. **Keep It Simple**:
   - Choose the simplest implementation that solves the problem
   - Consider functional implementations for simpler cases

4. **Consider Testability**:
   - Patterns should make your code more testable, not less
   - Dependency injection is often key to making patterns testable

### Common Pitfalls

1. **Pattern Overuse**:
   - Don't use patterns just to use patterns
   - "Design pattern hammer syndrome" - seeing everything as a nail

2. **Premature Abstraction**:
   - Implementing patterns before they're needed adds unnecessary complexity
   - Follow the "Rule of Three" - wait until you need the same code in three places

3. **Rigid Implementations**:
   - Being too dogmatic about "textbook" implementations
   - Not adapting patterns to your specific context

4. **Ignoring Language Features**:
   - Not leveraging Python-specific features that might simplify pattern implementation
   - Blindly copying patterns from statically typed languages

## Conclusion

Design patterns are powerful tools for solving common software design problems. They provide tested, proven development paradigms that can help you write more maintainable, flexible, and robust code. The examples we've examined (Observer, Strategy, and Template Method) represent just a few of the many useful patterns available to developers.

Remember that patterns are guidelines, not rules. The best developers understand when to apply patterns, when to adapt them, and sometimes when to avoid them altogether in favor of simpler solutions.

By understanding these patterns and their variations (both functional and object-oriented), you'll have powerful tools to address design challenges in your own code.
