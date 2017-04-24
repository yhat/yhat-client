#!/bin/bash

set -ex

if [[ "$2" == "rc" ]]; then
  bucket_name="yhat-conda-channel-rc"
else
  bucket_name="yhat-conda-channel"
fi

mkdir ~/${bucket_name}
mkdir -p ~/${bucket_name}/pkg/free
cd ~/${bucket_name}

bucket=s3://${bucket_name}
aws s3 sync $bucket .

pkgname="yhat"
pkgversion=$(python -c "from yhat import version; print(version.__version__)")
echo "building ${pkgname} ${pkgversion}"

# build conda for default OS and then cross-compile for other OS
mkdir ~/conda-builds/
conda package --pkg-name "$pkgname" --pkg-version "$pkgversion"
conda convert --platform  linux-64  "./yhat-${pkgversion}-py27_0.tar.bz2" -o ~/conda-builds/
conda convert --platform  linux-32  "./yhat-${pkgversion}-py27_0.tar.bz2" -o ~/conda-builds/
conda convert --platform  osx-64  "./yhat-${pkgversion}-py27_0.tar.bz2" -o ~/conda-builds/

# index for the conda <=4.0 format
cd ~/${bucket_name}
rm ./yhat*
cp -R ~/conda-builds/* ./
conda index ./linux-64
conda index ./linux-32
conda index ./osx-64
conda index ./win-64
conda index ./win-32

# index for the conda 4.2+ format
cd ~/${bucket_name}/pkg/free
cp -R ~/conda-builds/* ./
conda index ./linux-64
conda index ./linux-32
conda index ./osx-64
conda index ./win-64
conda index ./win-32

cd ~/${bucket_name}
tree .


if [[ "$2" == "rc" ]]; then
  aws s3 sync . $bucket/
fi

if [[ "$1" == "upload" ]]; then
  aws s3 sync . $bucket/
fi
