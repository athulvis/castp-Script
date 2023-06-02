import requests
import time
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC 
from biopandas.pdb import PandasPdb
import pandas as pd
import argparse
import sys
import base64


parser = argparse.ArgumentParser("Compares CASTP and PDB table and gets similar x,y, z")
parser.add_argument("-p", "--pdb", required=True, type = str, help= 'Protein file name in pdb format.')
parser.add_argument("-r","--radius", required=False, type=str, help='Value for radius probe. between 0.0 and 10.0')
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

url = 'http://sts.bioe.uic.edu/castp/submit_calc.php'
headers = {
    'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:102.0) Gecko/20100101 Firefox/102.0',
    'Accept': '*/*',
    'Accept-Language': 'en-US,en;q=0.5',
    'Accept-Encoding': 'gzip, deflate',
    'X-Requested-With': 'XMLHttpRequest',
    'Origin': 'http://sts.bioe.uic.edu',
    'DNT': '1',
    'Connection': 'keep-alive',
    'Referer': 'http://sts.bioe.uic.edu/castp/calculation.html'
}
files = {
    'file': (args.pdb, file, 'application/x-aportisdoc'),
}
data = {
    'probe': radius,
    'email': 'null'
}

response = requests.post(url, headers=headers, data=data, files=files)

job_id = str(response.text)

print(job_id)
file.close()
time.sleep(10)


if sys.platform == "linux" or sys.platform == "linux2":
    driver = webdriver.Firefox()
elif sys.platform == "win32":
    from selenium.webdriver.firefox.options import Options
    options = Options()
    options.binary_location = r'C:\Program Files\Mozilla Firefox\firefox.exe'
    driver = webdriver.Firefox(executable_path=r'C:\WebDrivers\geckodriver.exe', options=options)
else:
    print("System not supported. **Program will stop.**")
    sys.exit()

if not driver:
    print("Webdriver not found. **Program will stop**")
    sys.exit()

url = "http://sts.bioe.uic.edu/castp/index.html?" + job_id

driver.get(url)
WebDriverWait(driver, 10).until(lambda d: d.execute_script("return document.readyState") == "complete")
#WebDriverWait(driver, 20).until(EC.invisibility_of_element_located((By.ID, "atom_table")))
WebDriverWait(driver, 10).until(
     EC.presence_of_element_located((By.XPATH,'//*[@id="poc_table"]'))
 )
time.sleep(wait_time)

canvas = driver.find_element(By.CSS_SELECTOR,"#undefined")
# get the canvas as a PNG base64 string
canvas_base64 = driver.execute_script("return arguments[0].toDataURL('image/png').substring(21);", canvas)
# decode
canvas_png = base64.b64decode(canvas_base64)

# save to a file
with open(f"{args.pdb.split('.')[0]}.png", 'wb') as f:
    f.write(canvas_png)

css_txt = driver.find_element(By.CSS_SELECTOR,".seqpanel")

with open(f"{args.pdb.split('.')[0]}_sequence.txt","w") as f:
    f.write(str(css_txt.text))

soup = BeautifulSoup(driver.page_source, 'html.parser')
table = soup.find_all('table', {'id':'atom_table'})
tr = table[0].find_all("tr")
data = []
for elem in tr[1:]:
    sub_data = []
    for sub_e in elem:
        try:
            if sub_e.get_text() != "\n":
                sub_data.append(sub_e.get_text())
        except:
            continue
        data.append(sub_data)


table2 = soup.find_all('table', {'id':'poc_table'})
tr2 = table2[0].find_all("tr")
data2 = []
for ele in tr2[1:]:
    sub_data2 = []
    for sub_e2 in ele:
        try:
            if sub_e2.get_text() != "\n":
                sub_data2.append(sub_e2.get_text())
        except:
            continue
        data2.append(list(set(sub_data2)))


driver.close()

with open(f"{args.pdb.split('.')[0]}_area_vol.txt","w") as f:
    f.write(str(data2))

df_csv = pd.DataFrame(data)
df_csv.drop_duplicates(inplace=True)

#df_csv.drop(df.index[0],axis=0, inplace=True)
df_csv.reset_index(drop=True, inplace=True)
print(df_csv)
ppdb_df =  PandasPdb().read_pdb(args.pdb)
df2 = ppdb_df.df['ATOM']
#df_csv = pd.read_csv(args.csv)
df_csv.columns = ["PocID", "Chain",	"residue_number","residue_name", "atom_name"]

dtype_dict = {"PocID":"int64", "Chain":str, "residue_number":"int64",
                "residue_name":str, "atom_name":str}

df_csv = df_csv.astype(dtype_dict)

output = pd.merge(df2, df_csv, on=["residue_number","residue_name", "atom_name"], how='inner')
new_out = output[["residue_name", "atom_name",'residue_number','x_coord', 'y_coord', 'z_coord']]

new_out.to_excel(f"{args.pdb.split('.')[0]}.xlsx")

with open(f"{args.pdb.split('.')[0]}.log","w") as f:
    f.write(str(output[['x_coord', 'y_coord', 'z_coord']].mean()))

print("files created succesfully")

