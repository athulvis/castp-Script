# castp-Script

A Python script to run [CASTp](http://sts.bioe.uic.edu/castp/calculation.html) code from the command line.

CASTp (expanded as Computer Atlas of Surface Topography of Proteins) is  an online tool used for finding surface pockets and internal cavities in proteins which are possibly active sites for ligand binding.

**This script uses selenium and geckodriver to load the webpage and parse it.**

**The script will take few seconds to run. An initial time delay of 10 seconds is added to avoid sending frequent requests to the website.**

## Instructions to Setup the script

- Clone this repository.
- Install `requirements.txt` using 

    ```pip install -r requirements.txt```

- Download geckodriver from the [github link](https://github.com/mozilla/geckodriver/releases) suitable for your OS.

- **Linux** users should isntall geckodriver in `/usr/local/bin`or in `/usr/bin`.

- **Windows** users should install firefox browser first at default location : ```C:\Program Files\Mozilla Firefox```
- Then install geckodriver at the location : ```C:\WebDrivers```

- change User-Agent from `headers`:
Line no. 35     `'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:102.0) Gecko/20100101 Firefox/102.0'`
change User-Agent with your browser's. For that, goto https://myhttpheader.com/. Copy User-Agent value from there and paste it here. 

## Instructions to run the script

- For help text, run :

    ```python castp.py -h```

- Input the protein file in pdb format as given below:

    ```python castp.py -p <<<protein name>>>```

- If you wish to mention radius probe, use `-r` or `--radius` arguement. Default value is _1.4_.
- If your network is slow, please set wait time to desired time. Use the tag `--wait` or `-w` with time in seconds. Default value is _10_.

- If the code run succeeds, output files will be generated in the folder.

- Output consists of:
    - Area and volume information.
    - Image of protein structure
    - Active sites and their information.
    - Protein sequence.


## References

-  Tian et al., Nucleic Acids Res. 2018. PMID: 29860391 DOI: 10.1093/nar/gky473. 
- Stackoverflow
- Chatgpt






