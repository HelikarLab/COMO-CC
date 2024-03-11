import rpy2.robjects.packages as rpackages
import rpy2.robjects as robjects
from rpy2.robjects.vectors import StrVector

from .como_utilities import stringlist_to_list

utils = rpackages.importr('utils')
utils.chooseCRANmirror(ind=1)

# Install R packages
packnames = (
    'BiocManager',
    'devtools',
    'zoo',
    'data.table', 'dplyr', 'ggplot2', 'pheatmap', 'readr', 'tibble', 'tidyr', 'tidyverse', 'sjmisc')

bio_pkgs = ('limma', 'edgeR', 'DESeq2', 'genefilter', 'biomaRt')

names_to_install = [x for x in packnames if not rpackages.isinstalled(x)]
bio_to_install = [x for x in bio_pkgs if not rpackages.isinstalled(x)]
if len(names_to_install) > 0:
    utils.install_packages(StrVector(names_to_install), dependencies = True)

if len(bio_to_install) > 0:
    for pkg in bio_to_install:
        robjects.r(f"BiocManager::install('{pkg}')")

if not rpackages.isinstalled('zFPKM'):
    robjects.r("devtools::install_github('babessell1/zFPKM')")