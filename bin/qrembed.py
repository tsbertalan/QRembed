import argparse
import qrcode
import os
import logging
import io
import zipfile
import subprocess
import tempfile
import shutil

try:
    from pylibdmtx.pylibdmtx import encode as dmtx_encode
    from PIL import Image
    HAS_DMTX = True
except ImportError:
    HAS_DMTX = False


def compress_file_if_smaller(input_file):
    with open(input_file, 'rb') as f:
        original = f.read()
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, 'w', zipfile.ZIP_DEFLATED) as zf:
        zf.writestr(os.path.basename(input_file), original)
    zipped = buf.getvalue()
    if len(zipped) < len(original):
        logging.info(f"Compression reduced size from {len(original)} to {len(zipped)} bytes.")
        return zipped, True
    else:
        logging.info(f"Compression did not reduce size ({len(original)} bytes, zipped {len(zipped)} bytes). Using original.")
        return original, False


def file_to_qr(input_file, output_file=None, compress=True):
    if compress:
        data, used_zip = compress_file_if_smaller(input_file)
    else:
        with open(input_file, 'rb') as f:
            data = f.read()
        used_zip = False
    qr = qrcode.QRCode(
        version=40,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(data)
    qr.make(fit=False)
    img = qr.make_image(fill_color="black", back_color="white")
    if not output_file:
        ext = '.qr.zip.png' if compress and used_zip else '.qr.png'
        output_file = os.path.splitext(input_file)[0] + ext
    img.save(output_file)
    logging.info(f"QR code saved to {output_file}")


def file_to_datamatrix(input_file, output_file=None, compress=True):
    if not HAS_DMTX:
        raise ImportError("pylibdmtx is not installed. Please install it to use DataMatrix encoding.")
    if compress:
        data, used_zip = compress_file_if_smaller(input_file)
    else:
        with open(input_file, 'rb') as f:
            data = f.read()
        used_zip = False
    encoded = dmtx_encode(data)
    img = Image.frombytes('RGB', (encoded.width, encoded.height), encoded.pixels)
    if not output_file:
        ext = '.datamatrix.zip.png' if compress and used_zip else '.datamatrix.png'
        output_file = os.path.splitext(input_file)[0] + ext
    img.save(output_file)
    logging.info(f"DataMatrix code saved to {output_file}")


def create_7z_volumes(input_file, volume_size, output_prefix=None):
    tempdir = tempfile.mkdtemp()
    if not output_prefix:
        output_prefix = os.path.splitext(os.path.basename(input_file))[0]
    archive_name = os.path.join(tempdir, f'{output_prefix}.7z')
    # 7z volume size must be a string like '2m' for 2 megabytes, '500k' for 500 kilobytes
    # We'll use 'b' for bytes
    vol_str = f'{volume_size}b'
    cmd = [
        '7z', 'a', '-t7z', f'-v{vol_str}', archive_name, input_file
    ]
    logging.info(f'Running: {" ".join(cmd)}')
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        raise RuntimeError(f'7z failed: {result.stderr}')
    vol_files = sorted([
        os.path.join(tempdir, f) for f in os.listdir(tempdir)
        if f.startswith(output_prefix) and f.endswith('.7z') or '.7z.' in f
    ])
    return vol_files


def main():
    loglevel = os.environ.get('LOGLEVEL', 'INFO').upper()
    logging.basicConfig(level=getattr(logging, loglevel, logging.INFO))
    parser = argparse.ArgumentParser(description="Embed a file or directory in QR/DataMatrix images using 7z volumes.")
    parser.add_argument('input_path', help='Path to the file or directory to embed')
    parser.add_argument('-o', '--output', help='Output image file (default: <input>.png)')
    parser.add_argument('--method', choices=['qr', 'datamatrix'], default='qr', help='Encoding method: qr or datamatrix (default: qr)')
    parser.add_argument('--chunked', action='store_true', help='Enable chunked archive mode (split file/dir into 7z volumes for multiple codes)')
    parser.add_argument('--chunk-size', type=int, default=2900, help='Chunk size in bytes (default: 2900 for QR, required for --chunked)')
    parser.add_argument('--retain-zips', action='store_true', help='Move 7z volume files to the target parent directory after encoding')
    args = parser.parse_args()
    if args.chunked:
        chunk_files = create_7z_volumes(args.input_path, args.chunk_size)
        logging.info(f'Wrote {len(chunk_files)} 7z volume files.')
        png_files = []
        for cf in chunk_files:
            output_file = cf + f'.{args.method}.png'
            if args.method == 'qr':
                file_to_qr(cf, output_file, compress=False)
            elif args.method == 'datamatrix':
                file_to_datamatrix(cf, output_file, compress=False)
            png_files.append(output_file)
        # Move PNGs to parent dir of input_path
        parent_dir = os.path.dirname(os.path.abspath(args.input_path))
        for png in png_files:
            dest = os.path.join(parent_dir, os.path.basename(png))
            if os.path.exists(dest):
                os.remove(dest)
            shutil.move(png, dest)
            logging.info(f'Moved {png} to {dest}')
        if args.retain_zips:
            for cf in chunk_files:
                dest = os.path.join(parent_dir, os.path.basename(cf))
                if os.path.exists(dest):
                    os.remove(dest)
                shutil.move(cf, dest)
                logging.info(f'Moved {cf} to {dest}')
    else:
        if args.method == 'qr':
            file_to_qr(args.input_path, args.output, compress=True)
        elif args.method == 'datamatrix':
            file_to_datamatrix(args.input_path, args.output, compress=True)

if __name__ == '__main__':
    main()
