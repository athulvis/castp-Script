# tests/test_zipfile.py
from pathlib import Path
import math
import pandas as pd
import pytest
import shutil

import castpfoldpy.client as client

EXPECTED = {"x_coord": 9.996343, "y_coord": 12.546925, "z_coord": 40.095170}
JOBID = "j_68e5495011fa9"
DATA_DIR = Path("data")


@pytest.fixture(scope="module")
def extracted_only(tmp_path_factory):
    """
    Extract ZIP into a temp directory
    """
    cl = client.CastpFoldClient()
    tmp_path = tmp_path_factory.mktemp("zip_extract")

    zip_src = DATA_DIR / f"{JOBID}.zip"
    zip_bytes = zip_src.read_bytes()
    zip_path, extract_path = cl.save_output(zip_bytes, output_path=tmp_path, jobid=JOBID)

    yield zip_path, extract_path

    shutil.rmtree(extract_path, ignore_errors=True)

def test_save_output_files_present(extracted_only):
    zip_path, extract_path = extracted_only
    assert extract_path.exists()


def test_compute_pockets_and_compare(extracted_only):
    _, extract_path = extracted_only
    cl = client.CastpFoldClient()
    pockets_csv, pockets_txt = cl.compute_pockets(extract_path, JOBID)
    assert pockets_csv.exists() and pockets_txt.exists()

    df = pd.read_csv(pockets_csv)
    means = {k: float(df[k].mean()) for k in ["x_coord", "y_coord", "z_coord"]}
    for k, v in EXPECTED.items():
        assert math.isclose(means[k], v, rel_tol=1e-2, abs_tol=1e-2), f"{k} mismatch: {means[k]} vs {v}"
