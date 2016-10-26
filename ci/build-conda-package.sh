#!/bin/bash

set -ex

mkdir ~/yhat-conda-channel
cd ~/yhat-conda-channel

bucket=s3://yhat-conda-channel/
aws s3 sync $bucket .

pkgname="yhat"
pkgversion=$(python -c "from yhat import version; print(version.__version__)")
echo "building ${pkgname} ${pkgversion}"

# build conda for default OS and then cross-compile for other OS
mkdir ~/conda-builds/
conda package --pkg-name "$pkgname" --pkg-version "$pkgversion"
conda convert --platform all "./yhat-${pkgversion}-py27_0.tar.bz2" -o ~/conda-builds/

cd ~/yhat-conda-channel
sudo cp -R ~/conda-builds/* ./
conda index --no-remove
tree .


if [[ "$1" == "upload" ]]; then
  aws s3 sync . $bucket/
fi
