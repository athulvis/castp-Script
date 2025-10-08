from typing import Optional, Tuple
from dataclasses import dataclass
import io
import requests
import time
import zipfile
import pandas as pd
from pathlib import Path
from tqdm import tqdm
from Bio.PDB import PDBParser

SUBMIT_URL = "https://cfold.bme.uic.edu/castpfold/submit_calc.php"
DOWNLOAD_URL = "https://cfold.bme.uic.edu/castpfold/data/tmppdb/{jobid}/processed/{jobid}.zip"


@dataclass
class CastpFoldResultPaths:
    jobid: str
    zip_path: Path
    extract_path: Path
    pockets_csv: Optional[Path] = None
    pockets_txt: Optional[Path] = None



class CastpFoldClient:

    def __init__(self, session: Optional[requests.Session] = None, timeout: int = 30):
        self.submit_url = SUBMIT_URL
        self.download_url = DOWNLOAD_URL
        self.session = session or requests.Session()
        self.timeout = timeout
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:102.0) Gecko/20100101 Firefox/102.0',
            'Accept': '*/*',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate, br, zstd',
            'X-Requested-With': 'XMLHttpRequest',
            'Origin': 'https://cfold.bme.uic.edu',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Referer': 'https://cfold.bme.uic.edu/castpfold/compute',
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'same-origin',
            'Priority': 'u=0'
            }

    def _verify_pdb(self, pdb: str) -> tuple[bool, str]:

        try:
            parser = PDBParser(PERMISSIVE=True, QUIET=False)
            parser.get_structure("castpfoldpy", pdb)
            return True, "PDB structure is validated."
        except Exception as e:
            return False, f"PDB parse error: {e}"

    def submit(self, pdb_path:Path, radius: float = 1.4, email = "N/A") -> str:

        if not pdb_path.exists():
            raise FileNotFoundError(f"PDB file not found: {pdb_path}")

        if not (0.0 <= float(radius) <= 5.0):
            raise ValueError("ERROR: Radius must be between 0.0 and 5.0 (Å)")

        pdb_size = pdb_path.stat().st_size

        if pdb_size > 2 * 1024 * 1024:
            raise SystemExit("PDB file size is greater than 2 MB")

        ok, msg = self._verify_pdb(pdb_path)
        if ok:
            print(msg)
        if not ok:
            raise SystemExit(f"PDB verification failed: {msg}")

        data = {'probe': radius,'email': email}
        files = {'file': (pdb_path.name, open(pdb_path, 'rb'), 'application/vnd.palm')}
        try:
            res = self.session.post(self.submit_url, headers = self.headers, data=data, files=files)
        finally:
            files["file"][1].close()

        res.raise_for_status
        j = res.json()
        jobid = str(j.get("jobid"))
        if not jobid or jobid.lower == "none":
            raise RuntimeError(f"Invalid jobid: {j}. Submit the PDF file again.")

        return jobid

    def _download_zip(self, jobid: str) -> Tuple[Optional[bytes], Optional[str]]:

        res = self.session.get(self.download_url.format(jobid=jobid), stream=True, timeout=self.timeout)
        if res.status_code != 200:
            return None, None

        content_type = res.headers.get("Content-Type","")
        buffer = io.BytesIO()
        for chunk in res.iter_content(chunk_size=8192):
            if chunk:
                buffer.write(chunk)
        return buffer.getvalue(), content_type

    def download_zip(self, jobid: str, wait: int = 20, extra_wait: int = 30, max_retries: int = 1) -> bytes:

        for _ in tqdm(range(max(wait, 0)), desc="waiting...", unit="second"):
            time.sleep(1)

        content, content_type = self._download_zip(jobid)
        if content and (content_type or "").startswith("application/zip"):
            return content

        print("file is not ready yet.")

        for _ in tqdm(range(extra_wait), desc="waiting a bit more...", unit="second"):
            time.sleep(1)

        last_err = None
        attempts = max(1, max_retries)

        for _ in range(attempts):
            content, content_type = self._download_zip(jobid)
            if content and (content_type or "").startswith("application/zip"):
                return content
            last_err = f"content_type={content_type!r}, content_present={bool(content)}"
            time.sleep(2)

        raise RuntimeError(f"ZIP not ready for job {jobid}; last check: {last_err}. Use download_only option to download the file later.")

    def save_output(self, zip_bytes: bytes, output_path: Path, jobid: str ) -> Tuple[Path, Path]:

        output_path.mkdir(parents=True, exist_ok=True)
        zip_path = output_path / f"{jobid}.zip"

        with open(zip_path, "wb") as f:
            f.write(zip_bytes)

        extract_path = output_path / jobid
        extract_path.mkdir(parents=True, exist_ok=True)
        with zipfile.ZipFile(zip_path, "r") as file:
            file.extractall(extract_path)
        return zip_path, extract_path

    def compute_pockets(self, extract_path: Path, jobid:str) -> Tuple[Path, Path]:

        poc_file = extract_path / f"{jobid}.poc"

        if not poc_file.exists():
            raise FileNotFoundError(f"Missing .poc file: {poc_file}")

        df = pd.read_csv(poc_file, sep = r"\s+",
                        names = ["atom", "atom_no", "residue_name", "atom_name",
                        'residue_number','x_coord', 'y_coord', 'z_coord',
                                        "val", "perc", "poc_id", "poc"],
                        engine = "python")

        output = df[df["poc_id"]==1]
        save_now = extract_path / jobid
        pockets_csv = Path(f"{save_now}_pockets.csv")
        new_out = output[["residue_name", "atom_name",'residue_number','x_coord', 'y_coord', 'z_coord']]
        new_out.to_csv(pockets_csv, index= False)

        pockets_txt = Path(f"{save_now}_xyz.txt")
        with open(pockets_txt,"w") as f:
            f.write(output[['x_coord', 'y_coord', 'z_coord']].mean().to_string())

        return pockets_csv, pockets_txt

    def run(self, pdb: Optional[Path] = None, out_dir:Optional[Path] = None, radius:float = 1.4,
            wait:int = 20, extra_wait :int = 30, max_retries: int = 1, compute_pockets:bool = False,
            email:str = "N/A",download_only:bool= False, submit_only:bool = False,
            jobid:str = None) -> CastpFoldResultPaths:

        if download_only:
            if jobid is not None:
                zip_bytes = self.download_zip(jobid, wait=wait, extra_wait=extra_wait, max_retries=max_retries)
            else:
                raise SystemExit("ERROR: To download already submitted job, jobid should be provided.")

        else:
            jobid = self.submit(pdb, radius=radius, email=email)
            print(f"job id for {pdb.name} is {jobid}")

            if out_dir is None:
                out_dir = pdb.parent

            submit_log = out_dir / f"{pdb.name}_submit.log"
            with open(submit_log, "w") as file:
                file.write(f"PDB file name : {pdb.name} \n JOB ID : {jobid}")

            print(f"job id is written to {submit_log} file.")

            if submit_only:
                raise SystemExit(f"SUCCESS: Job submitted succesfully. Please note the job id: {jobid} for downloading later.")

            zip_bytes = self.download_zip(jobid, wait=wait, extra_wait=extra_wait, max_retries=max_retries)

        zip_path, extract_path = self.save_output(zip_bytes, output_path=out_dir, jobid=jobid)

        pockets_csv = None
        pockets_txt = None
        if compute_pockets:
            pockets_csv, pockets_txt = self.compute_pockets(extract_path, jobid)

        print("Output files created succesfully")
        return CastpFoldResultPaths(jobid=jobid, zip_path=zip_path, extract_path=extract_path, pockets_csv=pockets_csv, pockets_txt=pockets_txt)











