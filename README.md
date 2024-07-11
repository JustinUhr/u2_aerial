# TIFF to JP2 and JPEG Converter

This Python script converts TIFF images in a given directory to JPEG2000 (JP2) and JPEG formats. It provides an option to specify the quality of the JPEG output.

**Note:** Depending on your hardware and the size of the input images, the conversion process may take quite some time; as much as several minutes per image.

## Installation

1. Clone the repository
2. Create a virtual environment and activate it (optional but recommended)
```bash
python3 -m venv ./env
source ./env/bin/activate
```
3. Install the required packages
```bash
pip install -r requirements.txt
```

## Usage

To use the script, you need to specify the input directory containing TIFF files and the output directory where the converted JP2 and JPEG files will be saved.

## Parameters

### Required
- `--input_dir` : Input directory containing TIFF files
- `--output_dir` : Output directory where the converted JP2 and JPEG files will be saved

### Optional
- `--quality` : Quality of the JPEG output. The value can either be an integer between 1 and 100 or one of the following presets: `web_low`, `web_medium`, `web_high`, `web_very_high`, `web_maximum`, `low`, `medium`, `high`, `maximum`. Default is 100.

- `--existing` : What to do if jp2 or jpeg file already exists, options are: `raise` an error, `skip` the file, `overwrite` the file. Default is `raise`.

## Examples

### Minimal Example
```bash
python compress_tiffs.py --input_dir /path/to/tiff_files --output_dir /path/to/output_dir
```

### Example with all parameters
```bash
python compress_tiffs.py --input_dir /path/to/tiff_files --output_dir /path/to/output_dir --quality 80 --existing overwrite
```