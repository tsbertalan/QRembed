import argparse
import qrcode
import os
import logging
import io
import zipfile

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


def main():
    loglevel = os.environ.get('LOGLEVEL', 'INFO').upper()
    logging.basicConfig(level=getattr(logging, loglevel, logging.INFO))
    parser = argparse.ArgumentParser(description="Embed a file's contents in a QR code or DataMatrix image.")
    parser.add_argument('input_file', help='Path to the file to embed')
    parser.add_argument('-o', '--output', help='Output image file (default: <input>.png)')
    parser.add_argument('--method', choices=['qr', 'datamatrix'], default='qr', help='Encoding method: qr or datamatrix (default: qr)')
    parser.add_argument('--no-compress', action='store_true', help='Do not compress file before embedding')
    args = parser.parse_args()
    compress = not args.no_compress
    if args.method == 'qr':
        file_to_qr(args.input_file, args.output, compress=compress)
    elif args.method == 'datamatrix':
        file_to_datamatrix(args.input_file, args.output, compress=compress)

if __name__ == '__main__':
    main()
