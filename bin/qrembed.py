import argparse
import qrcode
import os
import logging


def file_to_qr(input_file, output_file=None):
    with open(input_file, 'rb') as f:
        data = f.read()
    # Use low error correction and max version
    qr = qrcode.QRCode(
        version=40,  # max version (largest QR code)
        error_correction=qrcode.constants.ERROR_CORRECT_L,  # lowest error correction
        box_size=10,
        border=4,
    )
    qr.add_data(data)
    qr.make(fit=False)  # Don't fit, raise if too large
    img = qr.make_image(fill_color="black", back_color="white")
    if not output_file:
        output_file = os.path.splitext(input_file)[0] + '.png'
    img.save(output_file)
    logging.info(f"QR code saved to {output_file}")


def main():
    loglevel = os.environ.get('LOGLEVEL', 'INFO').upper()
    logging.basicConfig(level=getattr(logging, loglevel, logging.INFO))
    parser = argparse.ArgumentParser(description="Embed a file's contents in a QR code image.")
    parser.add_argument('input_file', help='Path to the file to embed')
    parser.add_argument('-o', '--output', help='Output PNG file (default: <input>.png)')
    args = parser.parse_args()
    file_to_qr(args.input_file, args.output)

if __name__ == '__main__':
    main()
