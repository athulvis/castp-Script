import requests
import time
import zipfile
import pandas as pd
import argparse
import sys
from pathlib import Path
from tqdm import tqdm

parser = argparse.ArgumentParser("Compares CASTP and PDB table and gets similar x,y, z")
parser.add_argument("-p", "--pdb", required=True, type = str, help= 'Protein file name in pdb format.')
parser.add_argument("-d", "--directory", required=False, type = str, help= 'directory to download castp files')
parser.add_argument("-r","--radius", required=False, type=str, help='Value for radius probe. between 0.0 and 10.0')
parser.add_argument("-f", '--flag', action='store_true', help='Use it if needed to calculate pocket coordinates')
parser.add_argument("-w","--wait", required=False, type=int, help='Wait time to load the page. Default is 10. Use 20 \
or more if internet is slow')

args = parser.parse_args()

file = open(args.pdb, 'rb')
if args.radius:
    radius = str(args.radius)
else:
    radius = '1.4'

if args.wait:
    wait_time = int(args.wait)
else:
    wait_time = 10

url = 'https://cfold.bme.uic.edu/castpfold/submit_calc.php'
headers = {
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
files = {
    'file': (args.pdb, file, 'application/vnd.palm'),
}
data = {
    'probe': radius,
    'email': 'N/A'
}

response = requests.post(url, headers=headers, data=data, files=files)

job_id = str(response.json()["jobid"])

print(job_id)
file.close()
for _ in tqdm(range(10), desc="waiting...", unit="second"):
    time.sleep(1)



downurl = "https://cfold.bme.uic.edu/castpfold/data/tmppdb/" + job_id + "/processed/" + job_id + ".zip"

downres = requests.get(downurl, stream=True)

content_type = downres.headers.get('Content-Type', '')

if content_type != 'application/zip':
    for _ in tqdm(range(30), desc="waiting a bit more...", unit="second"):
        time.sleep(1)

downres = requests.get(downurl, stream=True)

savename = job_id +".zip"
if args.directory:
    save_path = Path(args.directory) / savename
    extract_path = Path(args.directory)/job_id
else:
    save_path = Path(args.pdb).parent / savename
    extract_path = Path(args.pdb).parent / job_id
if downres.status_code == 200:
    with open(save_path, 'wb') as file:
            for chunk in downres.iter_content(chunk_size=512):
                file.write(chunk)


extract_path.mkdir(parents=True, exist_ok=True)
with zipfile.ZipFile(save_path, 'r') as zip_ref:
    zip_ref.extractall(extract_path)

if args.flag:
    poc = job_id +".poc"

    df = pd.read_csv(extract_path/poc, sep='\s+', names=["atom", "atom_no", "residue_name", "atom_name",
                        'residue_number','x_coord', 'y_coord', 'z_coord',
                                        "val", "perc", "poc_id", "poc"])

    output = df[df["poc_id"]==1]
    save_now = extract_path / job_id
    new_out = output[["residue_name", "atom_name",'residue_number','x_coord', 'y_coord', 'z_coord']]
    new_out.to_excel(f"{save_now}_pockets.xlsx")

    with open(f"{save_now}.log","w") as f:
        f.write(str(output[['x_coord', 'y_coord', 'z_coord']].mean()))

print("files created succesfully")


