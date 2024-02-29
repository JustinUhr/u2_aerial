import os
import sys
import argparse
from PIL import Image, ImageFile
from tqdm import tqdm

# setup logging
import logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
log = logging.getLogger(__name__)
# set the location of the log file
log_file = 'compress_tiffs.log'
log.addHandler(logging.FileHandler(log_file))

log.info("Starting compress_tiffs.py")

# Increase the maximum image pixel limit
Image.MAX_IMAGE_PIXELS = 200000000
# ImageFile.LOAD_TRUNCATED_IMAGES = True
                                 

def open_image(input_path):   
    # Open the image
    img = Image.open(input_path)
    return img

def make_jp2(img, output_path):
    # Convert to jp2
    img.save(output_path, format='JPEG2000')

def make_jpeg(img, output_path, quality=100):
    # Check the mode of the image
    # print(f"Image mode: {img.mode}")

    # Convert from 16-bit grayscale to 8-bit grayscale
    img = img.point(lambda p: p * (255/65535)).convert('L')

    # print(f"Image mode after conversion: {img.mode}")

    # Convert to RGB if not already
    if img.mode != 'RGB':
        img = img.convert('RGB')

    # print(f"Image mode after conversion to RGB: {img.mode}")

    # Convert to jpeg
    img.save(output_path, format='JPEG', quality=quality)

def both_images_already_exist(tiff_file, output_dir):
    jp2_path = os.path.join(output_dir, tiff_file.replace('.tiff', '.jp2'))
    jp2_path = jp2_path.replace('.tif', '.jp2')
    jpeg_path = os.path.join(output_dir, tiff_file.replace('.tiff', '.jpeg'))
    jpeg_path = jpeg_path.replace('.tif', '.jpeg')
    if os.path.exists(jp2_path) and os.path.exists(jpeg_path):
        return True
    return False

if __name__ == "__main__":
    # get args
    parser = argparse.ArgumentParser(description='Convert tiff images in a given directory to jp2 and jpeg')
    parser.add_argument('input_dir', type=str, help='input directory of tiff images to be converted to jp2 and jpeg')
    parser.add_argument('output_dir', type=str, help='output directory where jp2 and jpeg images will be saved, will be created if not exists')
    parser.add_argument('--quality', type=str, default=100, help='quality of jpeg image, default is 100')
    parser.add_argument('--existing', type=str, default='raise', help='what to do if jp2 or jpeg file already exists, options are: raise, skip, overwrite. Default is raise.')
    args = parser.parse_args()
    input_dir = args.input_dir
    output_dir = args.output_dir
    quality = args.quality

    # Check if quality is a valid number or preset
    if not quality.isdigit() and quality not in ['web_low', 'web_medium', 'web_high', 'web_very_high', 'web_maximum', 'low', 'medium', 'high', 'maximum']:
        raise Exception("Invalid value for --quality, options are: number between 1 and 100, or: web_low, web_medium, web_high, web_very_high, web_maximum, low, medium, high, maximum") 

    if args.existing not in ['raise', 'skip', 'overwrite']:
        raise Exception("Invalid value for --existing, options are: raise, skip, overwrite")

    # Check if input directory exists
    if not os.path.exists(input_dir):
        print("Input directory does not exist")
        sys.exit(1)

    # Create output directory if it does not exist
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    # Get all tiff files in input directory
    # extension might be .tiff or .tif
    tiff_files = [f for f in os.listdir(input_dir) if f.endswith('.tif') or f.endswith('.tiff')]
    if args.existing == 'skip':
        tiff_files = [f for f in tiff_files if not both_images_already_exist(f, output_dir)]

    for tiff_file in tqdm(tiff_files):
        tiff_path = os.path.join(input_dir, tiff_file)
        # print(f'tiff_path: {tiff_path}')
        jp2_path = os.path.join(output_dir, tiff_file.replace('.tiff', '.jp2'))
        jp2_path = jp2_path.replace('.tif', '.jp2')
        # print(f'jp2_path: {jp2_path}')
        jpeg_path = os.path.join(output_dir, tiff_file.replace('.tiff', '.jpeg'))
        jpeg_path = jpeg_path.replace('.tif', '.jpeg')
        # print(f'jpeg_path: {jpeg_path}')

        if args.existing == 'skip':
            if os.path.exists(jp2_path) and os.path.exists(jpeg_path):
                log.debug(f"Skipping {tiff_file} as jp2 and jpeg files already exist")
                continue
        elif args.existing == 'overwrite':
            if os.path.exists(jp2_path):
                log.debug(f"Overwriting {jp2_path}")
                os.remove(jp2_path)
            if os.path.exists(jpeg_path):
                log.debug(f"Overwriting {jpeg_path}")
                os.remove(jpeg_path)
        else:
            # if jp2 or jpeg file already exists, raise an error
            if os.path.exists(jp2_path) or os.path.exists(jpeg_path):
                log.debug(f"Both jp2 and jpeg files already exist for {tiff_file}")
                raise Exception(f"Both jp2 and jpeg files already exist for {tiff_file}")

        # # Open the tiff image
        # img = open_image(tiff_path)

        # Convert to jp2 and jpeg
        make_jp2(tiff_path, jp2_path)
        make_jpeg(tiff_path, jpeg_path, quality=quality)
        # print(f"Converted {tiff_file} to jp2 and jpeg")
    print("Done")