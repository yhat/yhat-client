#!/bin/bash

set -ex

bucket_name="yhat-conda-channel"

mkdir ~/${bucket_name}
cd ~/${bucket_name}

bucket=s3://${bucket_name}/
aws s3 sync $bucket .

pkgname="yhat"
pkgversion=$(python -c "from yhat import version; print(version.__version__)")
echo "building ${pkgname} ${pkgversion}"

# build conda for default OS and then cross-compile for other OS
mkdir ~/conda-builds/
conda package --pkg-name "$pkgname" --pkg-version "$pkgversion"
conda convert --platform all "./yhat-${pkgversion}-py27_0.tar.bz2" -o ~/conda-builds/

cd ~/${bucket_name}
sudo cp -R ~/conda-builds/* ./
conda index --no-remove
tree .


if [[ "$1" == "upload" ]]; then
  aws s3 sync . $bucket/
fi
