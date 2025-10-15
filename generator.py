import random

def generate_operations(count=30):
    operations = []
    while len(operations) < count:
        op_type = random.choice(['+', '-', '*', '/'])
        if op_type == '+':
            a = random.randint(1, 99)
            b = random.randint(1, 100 - a)
            result = f"{a} + {b}"
        elif op_type == '-':
            a = random.randint(2, 100)
            b = random.randint(1, a - 1)
            result = f"{a} - {b}"
        elif op_type == '*':
            a = random.randint(1, 10)
            b = random.randint(1, 10)
            if a * b <= 100:
                result = f"{a} * {b}"
            else:
                continue
        elif op_type == '/':
            b = random.randint(1, 10)
            a = b * random.randint(1, 10)
            result = f"{a} / {b}"
        operations.append(result)
    return operations



