import os, sys
import argparse
import time

import numpy as np

from PIL import Image, ImageFile
import cv2
import imageio.v3 as iio
import io

from tqdm import tqdm

# from memory_profiler import profile
# import gc
# import objgraph

# setup logging - don't log to console
import logging

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%d/%b/%Y %H:%M:%S',
    filename='compress_tiffs.log',
    filemode='w'
)
log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)

# # log to console
ch = logging.StreamHandler()
ch.setLevel(logging.INFO)
log.addHandler(ch)

# logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
# log = logging.getLogger(__name__)
# # set the location of the log file
# log_file = 'compress_tiffs.log'
# log.addHandler(logging.FileHandler(log_file))

log.info("Starting compress_tiffs.py")

# Increase the maximum image pixel limit
Image.MAX_IMAGE_PIXELS = 200000000
# ImageFile.LOAD_TRUNCATED_IMAGES = True
                            
# @profile
def make_jp2(input_path, output_path):
    # Convert to jp2 using opencv
    log.debug(f"Converting {input_path} to jp2")
    try:
        img = cv2.imread(input_path, cv2.IMREAD_UNCHANGED)
        log.debug(f"Image shape: {img.shape}")
        cv2.imwrite(output_path, img, [int(cv2.IMWRITE_JPEG2000_COMPRESSION_X1000), 1000])
        log.debug(f"Converted {input_path} to jp2")
    except Exception as e:
        log.error(f"Error compressing image: {e}")

# def make_jp2(input_path, output_path):
#     img = iio.imread(input_path)
#     if img.dtype == np.uint16:
#         img = img.astype(np.uint8)

#     # Convert to jp2
#     output = io.BytesIO()
#     iio.imwrite(output, img, plugin='opencv', extension='.jp2', params=[int(cv2.IMWRITE_JPEG2000_COMPRESSION_X1000), 1000])

#     # Save the output to a file
#     with open(output_path, 'wb') as f:
#         f.write(output.getvalue())

# def make_jp2(input_path, output_path):
#     # Use imageio to read the image
#     img = iio.imread(input_path)

#     # Convert to jp2
#     iio.imwrite(output_path, img, extension=".jp2")

# @profile
def make_jpeg(input_path, output_path, quality='100'):
    # Convert quality to an integer if it is a numberic string
    if quality.isdigit():
        quality = int(quality)

    log.debug(f"Converting {input_path} to jpeg")
    # Use imageio to read the image
    try:
        img = iio.imread(input_path)
        log.debug(f"Image shape: {img.shape}")
    except Exception as e:
        log.error(f"Error reading image: {e}")
        return

    # Scale the image to 50%
    try:
        img = cv2.resize(img, (0, 0), fx=0.5, fy=0.5)
        log.debug(f"Image shape after scaling: {img.shape}")
    except Exception as e:
        log.error(f"Error scaling image: {e}")
        return

    # Make an even smaller version for the thumbnail
    try:
        thumbnail = cv2.resize(img, (0, 0), fx=0.2, fy=0.2)
        log.debug(f"Thumbnail shape: {thumbnail.shape}")
    except Exception as e:
        log.error(f"Error creating thumbnail: {e}")
        return

    # Convert the numpy array from 16-bit to 8-bit
    # Base this on the method used in PIL which is ```img = img.point(lambda p: p * (255/65535)).convert('L')`
    try:
        img = img * (255/65535)
        log.debug(f"Image shape after conversion: {img.shape}")
        img = img.astype('uint8')
        log.debug(f"Image shape after conversion to uint8: {img.shape}")
    except Exception as e:
        log.error(f"Error converting image: {e}")
        return
    
    # Do the same for the thumbnail
    try:
        thumbnail = thumbnail * (255/65535)
        log.debug(f"Thumbnail shape after conversion: {thumbnail.shape}")
        thumbnail = thumbnail.astype('uint8')
        log.debug(f"Thumbnail shape after conversion to uint8: {thumbnail.shape}")
    except Exception as e:
        log.error(f"Error converting thumbnail: {e}")
        return
    
    # Use Pillow to save the thumbnail directly, no need to use imageio
    try:
        thumbnail = Image.fromarray(thumbnail)
        thumbnail.save(output_path.replace('.jpeg', '_thumbnail.jpeg'), format='JPEG', quality=quality)
        log.debug(f"Thumbnail saved to file: {output_path.replace('.jpeg', '_thumbnail.jpeg')}")
    except Exception as e:
        log.error(f"Error saving thumbnail: {e}")
        return
    
    # Use imageio to write the image to a jpeg file

    # Create a BytesIO object to write the image to
    output = io.BytesIO()
    try:
        # Write the image to the BytesIO object
        log.debug(f"Writing image to jpeg file: {output_path}")
        iio.imwrite(output, img, plugin="pillow", extension=".jpeg", quality=quality)
        log.debug(f"Image written to jpeg file: {output_path}")

        # Save the output to a file
        log.debug(f"Saving image to file: {output_path}")
        with open(output_path, 'wb') as f:
            f.write(output.getvalue())
        log.debug(f"Image saved to file: {output_path}")
    except Exception as e:
        log.error(f"Error: {e}")
    finally:
        output.close()
        log.debug(f"Closed BytesIO object")

    # objgraph.show_refs([img], filename='refs.png')
    # gc.collect()
    # print(gc.get_stats())


## @profile
# def make_jpeg_no_streaming(input_path, output_path, quality=100):
#     # add 'test' to the file name to test the memory usage
#     output_path = output_path.replace('.jpeg', '_test.jpeg')

#     # Use large_image_to_jpeg for files over 700 MB

#     img = Image.open(input_path)

#     # Convert from 16-bit grayscale to 8-bit grayscale
#     img = img.point(lambda p: p * (255/65535)).convert('L')

#     # print(f"Image mode after conversion: {img.mode}")

#     # Convert to RGB if not already
#     if img.mode != 'RGB':
#         img = img.convert('RGB')

#     # print(f"Image mode after conversion to RGB: {img.mode}")

#     # Convert to jpeg
#     img.save(output_path, format='JPEG', quality=quality)

#     # Clean up
#     img.close()
#     img = None

# @profile
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
    parser.add_argument('--input_dir', type=str, required=True, help='input directory of tiff images to be converted to jp2 and jpeg')
    parser.add_argument('--output_dir', type=str, required=True, help='output directory where jp2 and jpeg images will be saved, will be created if not exists')
    parser.add_argument('--quality', type=str, default='100', 
                        help='quality of thumbnail image, default is 100. '
                        'You may also use one of the following presets: '
                        'web_low, web_medium, web_high, web_very_high, '
                        'web_maximum, low, medium, high, maximum.')
    parser.add_argument('--existing', type=str, default='raise', help='what to do if jp2 or jpeg file already exists, options are: raise, skip, overwrite. Default is raise.')
    args = parser.parse_args()
    input_dir: str = args.input_dir
    output_dir: str = args.output_dir
    quality: str = args.quality

    # Check if quality is a valid number or preset
    if (not quality.isdigit() and 
        quality not in ['web_low', 'web_medium', 'web_high', 'web_very_high', 
                        'web_maximum', 'low', 'medium', 'high', 'maximum']):
        raise Exception("Invalid value for --quality, options are: an integer between 1 and 100, or: web_low, web_medium, web_high, web_very_high, web_maximum, low, medium, high, maximum") 

    # If quality is a number, confirm it is between 1 and 100
    if quality.isdigit():
        int_quality = int(quality)
        if int_quality < 1 or int_quality > 100:
            raise Exception("Quality must be between 1 and 100")

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
            if both_images_already_exist(tiff_file, output_dir):
                log.debug(f"Skipping {tiff_file} as jp2 and jpeg files already exist")
                continue
        elif args.existing == 'overwrite':
            if os.path.exists(jp2_path):
                log.debug(f"Overwriting {jp2_path}")
                os.remove(jp2_path)
            if os.path.exists(jpeg_path):
                log.debug(f"Overwriting {jpeg_path}")
                os.remove(jpeg_path)
            if os.path.exists(jpeg_path.replace('.jpeg', '_thumbnail.jpeg')):
                log.debug(f"Overwriting {jpeg_path.replace('.jpeg', '_thumbnail.jpeg')}")
                os.remove(jpeg_path.replace('.jpeg', '_thumbnail.jpeg'))
        else:
            # if jp2 or jpeg file already exists, raise an error
            if os.path.exists(jp2_path) or os.path.exists(jpeg_path):
                log.debug(f"Both jp2 and jpeg files already exist for {tiff_file}")
                raise Exception(f"Both jp2 and jpeg files already exist for {tiff_file}")

        # # Open the tiff image
        # img = open_image(tiff_path)

        # Convert to jp2 and jpeg
        make_jp2(tiff_path, jp2_path)
        log.info(f"Converted {tiff_file} to jp2")
        # time.sleep(20)

        make_jpeg(tiff_path, jpeg_path, quality=quality)
        log.info(f"Converted {tiff_file} to jpeg")
        # time.sleep(20)
        # make_jpeg_no_streaming(tiff_path, jpeg_path, quality=quality)
        # print(f"Converted {tiff_file} to jp2 and jpeg")
    print("Done")