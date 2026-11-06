import random

def extract_code(text):
    text=text.strip()
    if text.startswith('```') and text.endswith('```'):
        return '\n'.join(text.splitlines()[1:-1]), False
    return text, True

def select_tasks(tasks, limit, seed):
    if limit < 1: raise ValueError('limit must be positive')
    tasks=sorted(tasks,key=lambda t:t['id'])
    random.Random(seed).shuffle(tasks)
    return tasks[:limit]
