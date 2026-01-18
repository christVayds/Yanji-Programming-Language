
class Exception:
    
    def __init__(self, message: str):
        self.message = message

class SyntaxError(Exception):
    def __init__(self, message: str):
        super().__init__(message)

    def __str__(self):
        return f'SyntaxError: {self.message}'
    
class TypeError(Exception):
    def __init__(self, message: str):
        super().__init__(message)

    def __str__(self):
        return f'TypeError: {self.message}'
    
class nameError(Exception):
    def __init__(self, message: str):
        super().__init__(message)

    def __str__(self):
        return f'NameError: {self.message}'
    
class divisionByZeroError(Exception):
    def __init__(self, message: str):
        self.message = message

    def __str__(self):
        return f'DivisionByZeroError: {self.message}'

class runtimeError(Exception):
    def __init__(self, message: str):
        self.message = message

    def __str__(self):
        return f'RuntimeError: {self.message}'

class memoryError(Exception):
    def __init__(self, message: str):
        self.message = message

    def __str__(self):
        return f'MemoryError: {self.message}'