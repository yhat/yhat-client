# Configure the conda environment and put it in the path using the
# provided versions

PYTHON_VERSION="$1"

ENVNAME="test-env-${PYTHON_VERSION}"

REQUIREMENTS="python=${PYTHON_VERSION} numpy"
conda create -n "${ENVNAME}" --quiet --yes $REQUIREMENTS
source activate "${ENVNAME}"
