import os
import sys
from PIL import Image
import qrembed

sizes = [32, 64, 128, 256, 384, 512]

methods = ['qr', 'datamatrix']

SRC_IMG = 'mandrill.tiff'

# Generate scaled images

def generate_scaled_image(filename, size):
    with Image.open(SRC_IMG) as img:
        img = img.resize((size, size), Image.LANCZOS)
        img.save(filename, format='JPEG')

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
            filename = f'mandrill_{size}px.jpg'
            generate_scaled_image(filename, size)
            print(f'Generated {filename} ({size}x{size})')
            if not try_embed(filename, method):
                print(f'Stopping {method} at {size}px')
                break
