import os
import subprocess
import argparse
import re

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("mesh_file", type=str, help="Mesh file path")
    ap.add_argument("-d", "--divisor", default=1, type=int, help="Sub-division level")
    ap.add_argument("-g", "--gradients", action='store_true', help="Compute gradients")
    ap.add_argument("-p", "--precision", default="single", choices=['single', 'double'])
    ap.add_argument("-i", "--input", default="./", help="Input folder")
    ap.add_argument("-o", "--output", default="./", help="Output folder")
    ap.add_argument("-t", "--type", default=".vtu", help="Output extension")
    ap.add_argument("pvd_name", type=str, help="Name of the PVD file")

    args = ap.parse_args()

    # gather
    input_dir = args.input
    output_dir = args.output
    
    # Get all .pyfrs files
    files = [f for f in os.listdir(input_dir) if f.endswith(".pyfrs")]
    
    # Sort them by the numeric part of the filename (robust sorting)
    # Extracts the last floating point number found in the filename
    def extract_time(f):
        match = re.search(r"([\d\.]+)\.pyfrs$", f)
        return float(match.group(1)) if match else 0.0

    files.sort(key=extract_time)

    if not files:
        print("No .pyfrs files found!")
        return

    # export
    print(f"Found {len(files)} files. Starting export...")
    
    valid_exports = []

    for i, fname in enumerate(files):
        in_path = os.path.join(input_dir, fname)
        out_name = fname.replace(".pyfrs", args.type)
        out_path = os.path.join(output_dir, out_name)
        
        # Build command
        cmd = ["pyfr", "export", "-d", str(args.divisor), "-p", args.precision]
        if args.gradients:
            cmd.append("-g")
        cmd.extend([args.mesh_file, in_path, out_path])

        print(f"[{i+1}/{len(files)}] Exporting {fname} -> {out_name}...")
        
        # Run SERIALLY to save RAM/CPU
        try:
            subprocess.check_call(cmd)
            valid_exports.append((extract_time(fname), out_name))
        except subprocess.CalledProcessError:
            print(f"Error exporting {fname}, skipping.")

    # write out
    pvd_file = os.path.join(output_dir, args.pvd_name)
    if not pvd_file.endswith(".pvd"):
        pvd_file += ".pvd"

    print(f"Writing PVD to {pvd_file}...")

    with open(pvd_file, "w") as f:
        f.write('<?xml version="1.0"?>\n')
        f.write('<VTKFile type="Collection" version="0.1" byte_order="LittleEndian">\n')
        f.write('  <Collection>\n')
        
        for t, fname in valid_exports:
            f.write(f'    <DataSet timestep="{t}" group="" part="0" file="{fname}"/>\n')
            
        f.write('  </Collection>\n')
        f.write('</VTKFile>\n')

    print("Done!")

if __name__ == "__main__":
    main()