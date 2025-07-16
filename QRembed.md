# QRembed

## Usage

Embed a file or directory in QR/DataMatrix images optionally using 7z volumes.

```sh
python bin/qrembed.py [-h] [-o OUTPUT] [--method {qr,datamatrix}] [--chunked] [--chunk-size CHUNK_SIZE] [--retain-zips] input_path
```

- `input_path`: Path to the file or directory to embed
- `-o OUTPUT, --output OUTPUT`: Output image file (default: <input>.png)
- `--method {qr,datamatrix}`: Encoding method: qr or datamatrix (default: qr)
- `--chunked`: Enable chunked archive mode (split file/dir into 7z volumes for multiple codes)
- `--chunk-size CHUNK_SIZE`: Chunk size in bytes (default: 2900 for QR, required for --chunked)
- `--retain-zips`: Move 7z volume files to the target parent directory after encoding

**Note:**

- Uses the largest QR code size and lowest error correction to maximize data capacity.
- If the file is too large to fit in a QR code, an error will be raised unless chunked mode is used.

Be warned--this doen't scale super well: a 10kB file took 4 (dense) QR codes, and I expect this is linear. But if your only data storage medium is physical QR codes, I guess this could be useful?

## Decoding

What seemed to work for me as to use [Binary Eye](https://github.com/markusfisch/BinaryEye) to download the QR codes directly to files, saving as FILENAME.7z.001 etc. (note the two periods). Then I could use [7Zipper](https://play.google.com/store/apps/details?id=org.joa.zipperplus7&hl=en-US&pli=1) to extract by starting with the 001th.

## Progress

- CLI can encode any file or directory as a series of QR or DataMatrix codes, using 7z volumes for multipart support.
- Default QR chunk size is set to 2900 bytes (empirically determined).
- Output PNGs and (optionally) 7z volumes are moved to the target's parent directory.
- Manual transfer and reassembly is possible, but tedious for large files.
- No standard for including filenames in QR payloads; most phone QR readers do not extract or display custom headers.

## Possible Next Steps

- Write a Python script to decode a folder of QR images and reassemble the original file/volume.
- Explore or build a mobile app for batch QR scanning and automatic reassembly.
- Add support for other 2D codes (e.g., Aztec) or optimize for text files.
- Improve error handling and user feedback for failed QR encodings.
- Add optional metadata (e.g., chunk number, total chunks) in a way that is easy to parse by custom tools.
- Document the decoding/reassembly process for users.
- Consider designing a minimal mobile "app" (e.g., a Python script, PWA, or small APK) that can be distributed via QR codes (ideally <10 QRs for the installer itself).
- This would enable fully offline, low-tech distribution of the decoding tool.
