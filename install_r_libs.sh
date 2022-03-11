R -e 'if (!requireNamespace("BiocManager", quietly = TRUE)) install.packages("BiocManager")'
R -e 'install.packages("devtools", dependencies=TRUE, repos="'"${CRAN_MIRROR}"'")'
R -e 'devtools::install_version("locfit", version="1.5-9.4", dependencies=TRUE, repos="'"${CRAN_MIRROR}"'")'
R -e 'BiocManager::install("edgeR", dep=TRUE, ask=FALSE)'
R -e 'devtools::install_github("babessell1/zFPKM", dependencies=TRUE, repos="'"${CRAN_MIRROR}"'")'
R -e 'install.packages("devtools", dependencies=TRUE, repos="'"${CRAN_MIRROR}"'")'
R -e 'BiocManager::install("affy", dep=TRUE, ask=FALSE)'
R -e 'BiocManager::install("agilp", dep=TRUE, ask=FALSE)'
R -e 'BiocManager::install("limma", dep=TRUE, ask=FALSE)'
R -e 'BiocManager::install("hgu133acdf", dep=TRUE, ask=FALSE)'
R -e 'install.packages(c("rzmq","repr","IRkernel","IRdisplay"), repos = c("http://irkernel.github.io/", getOption("repos")), type = "source")'
R -e 'install.packages(c("tidyverse", "sjmisc", "openxlsx", "countToFPKM"), dependencies=TRUE, repos="'"${CRAN_MIRROR}"'")'
R -e 'BiocManager::install("genefilter", dep=TRUE, ask=FALSE)'
#R -e 'BiocManager::install("biomaRt", dep=TRUE, ask=FALSE)'
#R -e 'BiocManager::install("edgeR", dep=TRUE, ask=FALSE)'
R -e 'BiocManager::install("DESeq2", dep=TRUE, ask=FALSE)'
#R -e 'BiocManager::install("zFPKM", dep=TRUE, ask=FALSE)'


#mkdir /home/"${NB_USER}"/rlibs
#chown -R "${NB_USER}" /home/"${NB_USER}"/rlibs
#R -e 'if (!requireNamespace("BiocManager", quietly = TRUE)) install.packages("BiocManager")'
#R -e 'BiocManager::install("affy", dep=TRUE, ask=FALSE, lib="/home/jupyteruser/rlibs")'
#R -e 'BiocManager::install("agilp", dep=TRUE, ask=FALSE, lib="/home/jupyteruser/rlibs")'
#R -e 'BiocManager::install("limma", dep=TRUE, ask=FALSE, lib="/home/jupyteruser/rlibs")'
#R -e 'BiocManager::install("hgu133acdf", dep=TRUE, ask=FALSE, lib="/home/jupyteruser/rlibs")'
#R -e 'install.packages(c("rzmq","repr","IRkernel","IRdisplay"), repos = c("http://irkernel.github.io/", getOption("repos")), type = "source", lib="/home/jupyteruser/rlibs")'
#R -e 'install.packages(c("tidyverse", "sjmisc"), dependencies=TRUE, repos="'"${CRAN_MIRROR}"'", lib="/home/jupyteruser/rlibs")'
#R -e 'BiocManager::install("genefilter", dep=TRUE, ask=FALSE, lib="/home/jupyteruser/rlibs")'
#R -e 'BiocManager::install("biomaRt", dep=TRUE, ask=FALSE, lib="/home/jupyteruser/rlibs")'
#R -e 'BiocManager::install("edgeR", dep=TRUE, ask=FALSE, lib="/home/jupyteruser/rlibs")'