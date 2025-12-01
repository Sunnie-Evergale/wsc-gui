#!/usr/bin/env python3
# cli.py
# Command-line interface for WSC decompiler

import argparse
import os
import sys
from pathlib import Path
from decompiler import decompile_wsc_file


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="WSC Decompiler - Extract and decode .WSC script files",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s input.wsc                    # Decompile to input.txt
  %(prog)s input.wsc -o output.txt      # Specify output file
  %(prog)s input.wsc -d output_dir/     # Output to directory
  %(prog)s *.wsc -d output_dir/         # Batch decompile all .wsc files
        """
    )

    parser.add_argument('input', nargs='+', help='Input .WSC file(s)')
    parser.add_argument('-o', '--output', help='Output file (for single input file)')
    parser.add_argument('-d', '--dir', help='Output directory (default: current directory)')
    parser.add_argument('-v', '--verbose', action='store_true', help='Verbose output')
    parser.add_argument('--version', action='version', version='WSC Decompiler 1.0')

    args = parser.parse_args()

    # Validate inputs
    for input_file in args.input:
        if not os.path.exists(input_file):
            print(f"Error: Input file '{input_file}' not found.", file=sys.stderr)
            return 1

        if not input_file.lower().endswith('.wsc'):
            print(f"Warning: '{input_file}' does not have .wsc extension", file=sys.stderr)

    # Determine output directory
    if args.dir:
        output_dir = Path(args.dir)
        if not output_dir.exists():
            output_dir.mkdir(parents=True, exist_ok=True)
            if args.verbose:
                print(f"Created output directory: {output_dir}")
    else:
        output_dir = Path.cwd()

    # Process files
    success_count = 0
    error_count = 0

    for input_file in args.input:
        input_path = Path(input_file)

        # Determine output file name
        if args.output and len(args.input) == 1:
            output_file = Path(args.output)
        else:
            output_file = output_dir / f"{input_path.stem}.txt"

        try:
            if args.verbose:
                print(f"Processing: {input_file}")
                print(f"  Output: {output_file}")

            decompile_wsc_file(str(input_path), str(output_file))
            success_count += 1

            if args.verbose:
                print(f"  ✓ Success")
            else:
                print(f"{input_file} -> {output_file}")

        except Exception as e:
            error_count += 1
            print(f"Error processing {input_file}: {e}", file=sys.stderr)
            if args.verbose:
                import traceback
                traceback.print_exc()

    # Summary
    total_files = len(args.input)
    if args.verbose or error_count > 0:
        print(f"\nSummary: {success_count}/{total_files} files processed successfully")
        if error_count > 0:
            print(f"Errors: {error_count}")

    return 0 if error_count == 0 else 1


if __name__ == "__main__":
    sys.exit(main())