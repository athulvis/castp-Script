# CASTpFoldpy
A Python script to run [CASTpFold](https://cfold.bme.uic.edu/castpfold/) code from the command line.


<!--toc:start-->
- [castpfoldpy](#castpfoldpy)
  - [Installation](#installation)
  - [About](#about)
  - [Instructions to run](#instructions-to-run)
    - [Operation modes](#operation-modes)
    - [Arguments](#arguments)
    - [Examples](#examples)
  - [References](#references)
<!--toc:end-->

## About
CASTpFold (expanded as Computer Atlas of Surface Topography of the universe of protein Folds) is  an online tool used for finding surface pockets and internal cavities in proteins which are possibly active sites for ligand binding.

**Please note that the CASTpFold analysis is done in the webserver provided by bme.uic.edu and this script is intended to run only from CLI, instead of accessing the website.**

**The script will take few seconds to run. An initial time delay of 10 seconds is added to avoid sending frequent requests to the website.**

**The maximum file size to upload is 2 MB.**

## Installation

Install castpfoldpy from PyPi using the command

  ```pip install castpfoldpy```

## Instructions to run
- For help text, run :
  
    ```python castp.py -h```
    
### Operation modes
This script allows to submit, download results separately as well as altogether using different modes.
- Submit only: uploads a PDB and prints the job id; no ZIP download and no pocket computation is performed in this mode.
- Download only: downloads a result ZIP using an existing job id; no submission is performed.
- Submit and download: uploads a PDB and then downloads the result ZIP.
### Arguments

- `-p`, `--pdb`: Protein file path in PDB format. Required for `--submit-only` or `--submit-download`.
- `-j`, `--jobid`: CASTpFold job ID to download (required for `--download-only`).
- `-d`, `--directory`: Directory to save the CASTpFold ZIP and extracted files.
- `-r`, `--radius`: Probe radius (Å) between 0.0 and 5.0 (default: **1.4**).
- `-pc`, `--pocket`: If set, compute pocket coordinates and write CSV/TXT file.
- `-w`, `--wait`: Initial wait time (seconds) before the first download attempt (default: **20**).
- `-ew`, `--extra-wait`: Extra wait time (seconds) before retrying when ZIP is not yet ready (default: **30**).
- `-t`, `--retries`: Number of extra download retries after extra-wait period (default: **1**).
- `--email`: Optional email passed to server. If provided, CASTpFold will send the download link to the email address. Default is **"N/A"**.

### Examples
1. **Download Only** (`-do`, `--download-only`): 
   
Download the results if the job ID is available. Requires `--job-id` argument.

  ```
  python castp.py --download-only -j <JOB_ID> -d /path/to/output
  ```
    
2. **Submit Only** (`-so`, `--submit-only`):
    
Uploads the PDB and prints the job ID. Results won't be downloaded. Requires `--pdb` argument.

  ```
  python castp.py --submit-only -p path/to/protein.pdb
  ```
    
3. **Submit and Download** (`-sd`, `--submit-download`): 
Uploads the PDB and then downloads the results. Requires `--pdb` argument.

  ```
  python castp.py --submit-download -p path/to/protein.pdb -d /path/to/output --pocket
  ```

- If the code run successfully, output files will be generated in the output folder provided.
- Output consists of:
    - Area and volume information.
    - Image of protein structure
    - Active sites and their information.
    - Protein sequence.
    
## Citations

Appreciate your citations if you are using this tool for your research purpose. Please cite the original CASTpFold paper along with this software.

**Plain Text format**

  ```
  Athul R T (Sahya Digital Conservation Foundation). CASTpFoldpy: Commandline tool to access CASTpFold server. Version 3.0, 2025. Repository: https://github.com/athulvis/castp-Script. DOI: 10.5281/zenodo.17292401

  Ye, B., Tian, W., Wang, B., and Liang, J. (2024). CASTpFold: Computed Atlas of Surface Topography of the universe of protein Folds. Nucleic Acids Research, 52(W1), W194–W199. https://doi.org/10.1093/nar/gkae415.
  ```

**BIBTEX format**

  ```  bibtex
  @software{CASTpFoldpy_zenodo_17292401,
    title        = {CASTpFoldpy : Commandline tool to access CASTpFold server},
    author       = {R T, Athul},
    year         = {2025},
    organization = {Sahya Digital Conservation Foundation},
    url          = {https://github.com/athulvis/castp-Script},
    doi          = {10.5281/zenodo.17292401},
    version      = {3.0},
    note         = {If you use this software, please cite it using the metadata from this file.},
  }
  
  @article{Ye2024CASTpFold,
  author  = {Ye, Bowei and Tian, Wei and Wang, Boshen and Liang, Jie},
  title   = {CASTpFold: Computed Atlas of Surface Topography of the universe of protein Folds},
  journal = {Nucleic Acids Research},
  volume  = {52},
  number  = {W1},
  pages   = {W194--W199},
  year    = {2024},
  doi     = {10.1093/nar/gkae415},
  url     = {https://doi.org/10.1093/nar/gkae415}
}

  ```


    
## References

- Ye, B., Tian, W., Wang, B., & Liang, J. (2024). CASTpFold: Computed Atlas of Surface Topography of the universe of protein Folds. Nucleic Acids Research, 52(W1), W194–W199. https://doi.org/10.1093/nar/gkae415 

- Fermi, G., & Perutz, M. F. (1984). THE CRYSTAL STRUCTURE OF HUMAN DEOXYHAEMOGLOBIN AT 1.74 ANGSTROMS RESOLUTION [Dataset]. In Worldwide Protein Data Bank. Worldwide Protein Data Bank. https://doi.org/10.2210/pdb4hhb/pdb 

