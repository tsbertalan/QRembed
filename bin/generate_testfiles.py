import os
import random
import sys
sys.path.insert(0, os.path.dirname(__file__))
import qrembed

sizes = [10, 100, 1000, 10000, 100000, 1000000, 10000000]

methods = [
    'datamatrix',
    'qr',
]

ASCII_CHARS = ''.join([chr(i) for i in range(32, 127)])  # printable ASCII

def generate_random_file(filename, size):
    with open(filename, 'w', encoding='ascii') as f:
        f.write(''.join(random.choices(ASCII_CHARS, k=size)))

def try_embed(filename, method):
    try:
        if method == 'qr':
            qrembed.file_to_qr(filename)
        elif method == 'datamatrix':
            qrembed.file_to_datamatrix(filename)
        print(f'Embedded {filename} with {method} successfully')
        return True
    except Exception as e:
        print(f'Failed to embed {filename} with {method}: {e}')
        return False

if __name__ == '__main__':
    for method in methods:
        print(f'\nTesting method: {method}')
        for size in sizes:
            filename = f'testfile_{size}B.txt'
            generate_random_file(filename, size)
            print(f'Generated {filename} ({size} bytes)')
            if not try_embed(filename, method):
                print(f'Stopping {method} at {size} bytes')
                break
