<div align="center">
  <img src="RUBALIZ_logo.png" alt="RUBALIZ_logo"/>
</div>

<br/>

<div align="center">
   <!-- Zenodo -->
  <a href="https://doi.org/10.5281/zenodo.6425451">
    <img src="https://zenodo.org/badge/doi/10.5281/zenodo.6425452.svg" alt="pypi" />
  </a>
</div>

<br/>

This repository aims to reproduce the results from Fuchs, Baumas et al. (2022).
Before proceeding, please install:
- Python https://www.python.org/downloads/
- Spyder https://www.anaconda.com/products/individual
- R https://cran.r-project.org/bin/windows/base/ and Rstudio https://www.rstudio.com/products/rstudio/download/
- The rubaliz package: https://github.com/RobeeF/rubaliz

Download this repository using GitHub Desktop or by downloading the zip directly.
To do so, click on the green "Code" menu in the top right and choose the desired option.  
The downloaded (and unzipped if needed) directory will be referred to as "root directory" in the sequel.
The root directory contains three subdirectories: the "Codes" repository fetch the data in the "Data" repository and reproduce the results in the "Results" directory.

Open the scripts in Spyder (for .py files) or Rstudio (for .R files), and adapt the path to the root file on your computer:
For Python scripts, the line to change is the "chdir" command of each script.
Example in Codes/rupture_main.py line 14:
```python
os.chdir('replace/this/path/with/the/root/directory/path/on/your/computer')
```

For R scripts, the line to change is the "setwd" command of each script.
Example in Codes/integration.R line 13:
```R
setwd('replace/this/path/with/the/root/directory/path/on/your/computer')
```
More information on how to use the RUBALIZ method for your use case can be found here:
https://github.com/RobeeF/rubaliz
