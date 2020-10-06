import sys
import argparse
import bpy

sys.path.append(".")
from range import Range

def render(args):
    # Clear existing objects.
    
    render = bpy.context.scene.render
    rpr = bpy.context.scene.rpr

    if args.out_path: 
        render.filepath = args.out_path

    if args.file_format:
        render.use_file_extension = True
        render.image_settings.file_format = args.file_format

    if args.render_width:
        render.resolution_x = int(args.render_width)

    if args.render_height:
        render.resolution_y = int(args.render_height)

    if args.min_samples:
        rpr.limits.min_samples = int(args.min_samples)

    if args.max_samples:
        rpr.limits.max_samples = int(args.min_samples)

    if args.noise_threshold:
        rpr.limits.noise_threshold = float(args.noise_threshold)
    
    if args.time_limit:
        rpr.limits.seconds = int(args.time_limit)

    bpy.ops.render.render(write_still=True)


def main():
    

    # get the args passed to blender after "--", all of which are ignored by
    # blender so script may receive their own arguments
    argv = sys.argv

    if "--" not in argv:
        argv = []  # as if no args are passed
    else:
        argv = argv[argv.index("--") + 1:]  # get all args after "--"

    # When --help or no args are given, print this help
    usage_text = (
        "Run blender in background mode with this script:"
        "  blender --background --python " + __file__ + " -- [options]"
    )

    parser = argparse.ArgumentParser(description=usage_text)

    parser.add_argument(
        "--out-path", dest="out_path",
    )
    parser.add_argument(
        "--width", dest="render_width", type=int,
    )
    parser.add_argument(
        "--height", dest="render_height", type=int,
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

    args = parser.parse_args(argv)

    if not argv:
        parser.print_help()
        return

    render(args)

    print("Batch job finished, exiting")

if __name__ == "__main__":
    main()
