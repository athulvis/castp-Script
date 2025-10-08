import sys
import traceback
import argparse
from typing import Optional
from pathlib import Path

from .client import CastpFoldClient

def argument_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="castpfoldpy",
        description="Submit a PDB to CASTpFold webserver, download results, and compute pocket coordinates.",
    )

    modes = p.add_mutually_exclusive_group(required=True)

    modes.add_argument("-do", "--download-only",
        action="store_true",
        help="Download the results if job id is available. --job-id argument is required.",)

    modes.add_argument(
        "-so", "--submit-only",
        action="store_true",
        help="Uploads PDB and prints job id. Results won't be downloaded. --pdb argument is required.",
    )

    modes.add_argument(
        "-sd", "--submit-download",
        action="store_true",
        help="Uploads PDB and then downloads the results. --pdb argument is required.",
    )


    p.add_argument("-p",
                "--pdb",
                type=str,
                help="Protein file path in PDB format. Required for --submit-only or --submit-download.")
    p.add_argument( "-j",
                "--jobid",
                type=str,
                help="CASTpFold job id to download (required for --download-only).",
    )
    p.add_argument("-d",
                "--directory",
                type=str,
                help="Directory to save the CASTpFold ZIP and extracted files.")
    p.add_argument("-r",
                "--radius",
                type=float,
                default = 1.4,
                help="Probe radius (Å) between 0.0 and 5.0; default 1.4.")
    p.add_argument("-pc",
                "--pocket",
                action= "store_true",
                help="If set, compute pocket coordinates (PocID==1) and write CSV/TXT file.")
    p.add_argument(
        "-w",
        "--wait",
        type=int,
        default = 20,
        help="Initial wait time (seconds) before first download attempt. Default 20.",
    )
    p.add_argument( "-ew",
        "--extra-wait",
        type=int,
        default=30,
        help="Extra wait time (seconds) before retrying when ZIP not yet ready. Default 30.",
    )
    p.add_argument( "-t",
        "--retries",
        type=int,
        default=1,
        help="Number of extra download retries after extra-wait period. Default 1.",
    )
    p.add_argument(
        "--email",
        type=str,
        default="N/A",
        help="Optional email passed to server. If provided, CastpFold will send the download link to email address.",
    )
    return p


def main(argv:Optional[list[str]] = None) -> int:

    parser = argument_parser()
    args = parser.parse_args(argv)

    if args.download_only:
        if not args.jobid:
            parser.error("--download-only option requires --job-id.")

    else:
        if not args.pdb:
            parser.error("--submit-only/--submit-download option requires --pdb")

    pdb_path = Path(args.pdb) if getattr(args, "pdb", None) else None
    out_dir = Path(args.directory) if args.directory else None
    client = CastpFoldClient()
    try:
        client.run(
            pdb=pdb_path if pdb_path is not None else Path("."),
            out_dir=out_dir,
            radius=float(args.radius),
            wait=int(args.wait),
            extra_wait=int(args.extra_wait),
            max_retries=int(args.retries),
            compute_pockets=bool(args.pocket),
            email=str(args.email),
            download_only=bool(args.download_only),
            submit_only=bool(args.submit_only),
            jobid=str(args.jobid) if getattr(args, "jobid", None) else None,)
        return 0
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
