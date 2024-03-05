import rpy2.robjects.packages as rpackages
from rpy2.robjects.vectors import StrVector

from .como_utilities import stringlist_to_list

utils = rpackages.importr('utils')
utils.chooseCRANmirror(ind=1)

# Install R packages
packnames = ('BiocManager', 'DESeq2', 'data.table', 'dplyr', 'ggplot2', 'pheatmap', 'readr', 'tibble', 'tidyr', 'tidyverse')
names_to_install = [x for x in packnames if not rpackages.isinstalled(x)]
if len(names_to_install) > 0:
    utils.install_packages(StrVector(names_to_install))
