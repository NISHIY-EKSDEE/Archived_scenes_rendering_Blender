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
        "Render archived scene with this script:"
        "python " + __file__ + " [options]"
    )

    parser = argparse.ArgumentParser(description=usage_text)

    parser.add_argument(
        "--source-path", dest="source_path", required=True
    )
    parser.add_argument(
        "--out-path", dest="out_path"
    )
    parser.add_argument(
        "--width", dest="render_width", type=int
    )
    parser.add_argument(
        "--height", dest="render_height", type=int
    )
    parser.add_argument(
        "--file-format", dest="file_format", 
        choices=['TGA', 'RAWTGA', 'JPEG', 'IRIS', 'IRIZ', 'AVIRAW', 'AVIJPEG', 'PNG', 'BMP',
         'HDR', 'TIFF', 'OPEN_EXR', 'OPEN_EXR_MULTILAYER', 'MPEG', 'CINEON', 'DPX', 'DDS', 'JP2']
    )
    parser.add_argument(
        "--min-samples", dest="min_samples", type=int
    )
    parser.add_argument(
        "--max-samples", dest="max_samples", type=int
    )
    parser.add_argument(
        "--noise-threshold", dest="noise_threshold", type=float, choices=Range(0.0, 1.0)
    )
    parser.add_argument(
        "--time-limit", dest="time_limit", type=int
    )

    args = parser.parse_args()
    args.source_path = os.path.abspath(args.source_path)

    if not os.path.exists(args.source_path):
        raise FileNotFoundError('Source file not found')

    if args.out_path:
        args.out_path = os.path.abspath(args.out_path)

        if not os.path.exists(args.out_path):
            raise FileNotFoundError('Output dir not found') 
    else:
        args.out_path = args.source_path

    tmp_dir_path = os.path.join(args.out_path, "tmp")

    with zipfile.ZipFile(args.source_path, 'r') as zip_ref:
        zip_ref.extractall(tmp_dir_path) 
        blend_file = None
        for entry in os.listdir(tmp_dir_path):
            if entry.endswith('.blend'):
                blend_file = os.path.join(tmp_dir_path, entry)
                cmd = generate_cmd(args, blend_file)
                execute_subprocess(args, cmd, os.path.join(args.out_path, f'{os.path.basename(blend_file)}.log'))

    shutil.rmtree(tmp_dir_path)
    print("script finished, exiting")

def generate_cmd(args, file):
    filename_without_ext = os.path.basename(os.path.splitext(file)[0])
    cmd = ['blender', '-b', file, '-E', 'RPR', '-P', 'background_render.py', '--', '--out-path', os.path.join(args.out_path, filename_without_ext)]
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