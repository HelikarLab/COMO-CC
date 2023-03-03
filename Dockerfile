FROM jupyter/r-notebook:latest

ARG GRB_SHORT_VERSION=10.0
ARG GRB_VERSION=10.0.0
ARG PYTHON_MAIN_VERSION=3.10
ARG PYTHON_SUB_VERSION=3.10.9

# Set gurobi environment variables
ENV GUROBI_HOME "${HOME}/gurobi/linux64"
ENV PATH "$PATH:$GUROBI_HOME/bin"
ENV LD_LIBRARY_PATH "$LD_LIBRARY_PATH:$GUROBI_HOME/lib"

COPY /environment.yaml "${HOME}/environment.yaml"
COPY --chown=1000:100 main "${HOME}"/main

# Install python-related items
RUN conda config --quiet --add channels conda-forge \
    && conda config --quiet --add channels bioconda \
    && conda config --quiet --add channels r \
    # Remove python from pinned versions; this allows us to update python. From: https://stackoverflow.com/a/11245372 \
    && sed -i "s|^python .*|python ${PYTHON_SUB_VERSION}|" /opt/conda/conda-meta/pinned \
    && mamba env update --quiet --name=base --file="${HOME}/environment.yaml" \
    && mamba clean --quiet --all --force-pkgs-dirs --yes \
    && R -e "devtools::install_github('babessell1/zFPKM')" \
    && jupyter trust "${HOME}/main/COMO.ipynb" \
    && rm -rf "${HOME}/environment.yaml"

# Install gurbori
RUN wget --quiet https://packages.gurobi.com/${GRB_SHORT_VERSION}/gurobi${GRB_VERSION}_linux64.tar.gz \
    && tar -xf gurobi${GRB_VERSION}_linux64.tar.gz \
    && rm -f gurobi${GRB_VERSION}_linux64.tar.gz \
    && mv -f gurobi* "${HOME}/gurobi"


# Update jupyter notebook configuration \
RUN echo "c.ServerApp.ip = '0.0.0.0'" >> "${HOME}/.jupyter/jupyter_notebook_config.py" \
    && echo "c.ServerApp.root_dir = '${HOME}/main'" >> "${HOME}/.jupyter/jupyter_notebook_config.py" \
    && echo "c.ServerApp.token = ''" >> "${HOME}/.jupyter/jupyter_notebook_config.py" \
    && echo "c.ServerApp.password = ''" >> "${HOME}/.jupyter/jupyter_notebook_config.py"

VOLUME /home/joyvan/main
