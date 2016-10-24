# Use the miniconda installer for faster download / install of conda
# itself
wget http://repo.continuum.io/miniconda/Miniconda-latest-Linux-x86_64.sh \
    -O ~/miniconda.sh
chmod +x ~/miniconda.sh && ~/miniconda.sh -b
export PATH=$HOME/miniconda2/bin:$PATH
echo $PATH
conda update --quiet --yes conda

# Configure the conda environment and put it in the path using the
# provided versions
REQUIREMENTS="python numpy"
echo "conda requirements string: $REQUIREMENTS"
conda create -n testenv27 --quiet --yes $REQUIREMENTS
source activate testenv27
