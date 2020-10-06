import sys     
import argparse
import os
import subprocess
import zipfile
import shutil
from range import Range

def main():
    # When --help or no args are given, print this help
    usage_text = (
        "Render archived scenes with this script:"
        "python " + __file__ + " [options]"
    )

    parser = argparse.ArgumentParser(description=usage_text)

    # Arguments for script
    parser.add_argument(
        "--source-path", dest="source_path", required=True, help="Path to .zip file"
    )
    parser.add_argument(
        "--out-path", dest="out_path", help="Path to put results to"
    )
    parser.add_argument(
        "--width", dest="render_width", type=int, help="Width of the resulting file"
    )
    parser.add_argument(
        "--height", dest="render_height", type=int, help="Height of the resulting file"
    )
    parser.add_argument(
        "--file-format", dest="file_format", help="Result file format",
        choices=['TGA', 'RAWTGA', 'JPEG', 'IRIS', 'IRIZ', 'AVIRAW', 'AVIJPEG', 'PNG', 'BMP',
         'HDR', 'TIFF', 'OPEN_EXR', 'OPEN_EXR_MULTILAYER', 'MPEG', 'CINEON', 'DPX', 'DDS', 'JP2']
    )
    parser.add_argument(
        "--min-samples", dest="min_samples", type=int,
        help="Minimum number of samples to render for each pixel. After this, adaptive sampling will stop sampling pixels where noise is less than threshold"
    )
    parser.add_argument(
        "--max-samples", dest="max_samples", type=int,
        help="Number of iterations to render for each pixel"
    )
    parser.add_argument(
        "--noise-threshold", dest="noise_threshold", type=float, choices=Range(0.0, 1.0),
        help="Cutoff for adaptive sampling. Once pixels are below this amount of noise, no more samples are added"
    )
    parser.add_argument(
        "--time-limit", dest="time_limit", type=int,
        help="Time limit in seconds for rendering a single scene"
    )

    args = parser.parse_args()
    args.source_path = os.path.abspath(args.source_path)

    if not os.path.exists(args.source_path):
        raise FileNotFoundError('Source file not found')
    
    if args.out_path:
        args.out_path = os.path.abspath(args.out_path)

        if not os.path.exists(args.out_path) or not os.path.isdir(args.out_path):
            raise FileNotFoundError('Output directory not found') 
    else:
        args.out_path = os.path.dirname(args.source_path)

    # Temporary directory to extract files to
    tmp_dir_path = os.path.join(args.out_path, "tmp")

    if zipfile.is_zipfile(args.source_path):
        with zipfile.ZipFile(args.source_path, 'r') as zip_ref:
            zip_ref.extractall(tmp_dir_path)
    else:
        raise FileNotFoundError('Source file is not .zip') 
    
    # Execute background rendering process for each .blend file in tmp directory
    for filename in os.listdir(tmp_dir_path):
            if filename.endswith('.blend'):
                blend_file = os.path.join(tmp_dir_path, filename)
                cmd = generate_cmd(args, blend_file)
                log_file = os.path.join(args.out_path, f'{filename}.log')
                execute_subprocess(args, cmd, log_file)

    # Deleting temporary directory
    shutil.rmtree(tmp_dir_path)
    print("Script finished, exiting")

def generate_cmd(args, file):
    filename_without_ext = os.path.basename(os.path.splitext(file)[0])
    out_path = os.path.join(args.out_path, filename_without_ext)
    cmd = ['blender', '-b', file, '-E', 'RPR', '-P', 'background_render.py', '--', '--out-path', out_path]
    if args.render_width:
        cmd.append('--width')
        cmd.append(str(args.render_width))
    if args.render_height:
        cmd.append('--height')
        cmd.append(str(args.render_height))
    if args.file_format:
        cmd.append('--file-format')
        cmd.append(args.file_format)
    if args.min_samples:
        cmd.append('--min-samples')
        cmd.append(str(args.min_samples))
    if args.max_samples:
        cmd.append('--max-samples')
        cmd.append(str(args.max_samples))
    if args.noise_threshold:
        cmd.append('--noise-threshold')
        cmd.append(str(args.noise_threshold))
    if args.time_limit:
        cmd.append('--time-limit')
        cmd.append(str(args.time_limit))
    return cmd

def execute_subprocess(args, cmd, log_file):
    with open(log_file, 'w') as log_file:
        process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, encoding="utf-8")
        stdout, stderr = process.communicate()
        log_file.write(stdout)
        

if __name__ == '__main__':
    main()