import os
import tempfile
import random
import qrembed

MIN_SIZE = 2950
MAX_SIZE = 20000
BYTES_STEP = 1

success_limit = None
fail_limit = None

def generate_random_file(path, size):
    with open(path, 'wb') as f:
        f.write(os.urandom(size))

def main():
    global success_limit, fail_limit
    with tempfile.TemporaryDirectory() as tmpdir:
        print(f"Testing in temp dir: {tmpdir}")
        for size in range(MIN_SIZE, MAX_SIZE + 1, BYTES_STEP):
            fname = os.path.join(tmpdir, f"test_{size}B.bin")
            generate_random_file(fname, size)
            try:
                qrembed.file_to_qr(fname, compress=False)
                print(f"Success: {size} bytes")
                success_limit = size
            except Exception as e:
                print(f"Fail: {size} bytes - {e}")
                fail_limit = size
                break
    print(f"Max successful QR size: {success_limit} bytes")
    if fail_limit:
        print(f"First failure at: {fail_limit} bytes")

if __name__ == '__main__':
    main()
