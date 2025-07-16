# QRembed

## Usage

Embed a file's contents in a QR code image (PNG):

```sh
python bin/qrembed.py <input_file> [-o output.png]
```

- `<input_file>`: Path to the file to embed in the QR code.
- `-o output.png`: (Optional) Output PNG file. Defaults to `<input_file>.png`.

**Note:**
- Uses the largest QR code size and lowest error correction to maximize data capacity.
- If the file is too large to fit in a QR code, an error will be raised.



