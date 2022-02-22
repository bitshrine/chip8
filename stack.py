class Stack:

    STACK_LIMIT = 16

    def __init__(self):
        self.stack = []

    def push(self, value):
        if (len(self.stack) < self.STACK_LIMIT):
            self.stack.append(value)

    def pop(self):
        return self.stack.pop()