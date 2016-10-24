# Use the miniconda installer for faster download / install of conda
# itself
wget http://repo.continuum.io/miniconda/Miniconda-latest-Linux-x86_64.sh \
    -O ~/miniconda.sh
chmod +x ~/miniconda.sh && ~/miniconda.sh -b
export PATH=$HOME/miniconda2/bin:$PATH
echo $PATH
conda update --quiet --yes conda
conda install -y conda-build
