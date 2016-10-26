#!/bin/bash

set -ex

bucket="yhat-conda-channel"
mkdir "~/${bucket}"
cd "~/${bucket}"

bucket="s3://$bucket/linux-64"
aws s3 sync $bucket .

pkgname="yhat"
pkgversion=$(python -c "from yhat import version; print(version.__version__)")
echo "building ${pkgname} ${pkgversion}"

# build conda for default OS and then cross-compile for other OS
mkdir ~/conda-builds/
conda package --pkg-name "$pkgname" --pkg-version "$pkgversion"
conda convert --platform all "./yhat-${pkgversion}-py27_0.tar.bz2" -o ~/conda-builds/
cd "~/${bucket}"
sudo cp -R ~/conda-builds/* ./
conda index --no-remove
tree .


if [[ "$1" == "upload" ]]; then
  aws s3 sync . $bucket/
fi
