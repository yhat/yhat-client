#!/bin/bash

set -ex

bucket="yhat-conda-channel"
mkdir "${bucket}"
cd "${bucket}"

bucket="s3://$bucket/linux-64"

pkgname="yhat"
pkgversion=$(python -c "from yhat import version; print(version.__version__)")
echo "building $pkg $pkgname $pkgversion"

aws s3 sync $bucket/.index.json .
aws s3 sync $bucket/repodata.json .
aws s3 sync $bucket/repodata.json.bz2 .
pip install $pkg
conda package --pkg-name "$pkgname" --pkg-version "$pkgversion"
conda index --no-remove
tree .

mkdir ~/conda-builds/
conda convert --platform all "./yhat-${pkgversion}-py27_0.tar.bz2" -o ~/conda-builds/
tree ~/conda-builds/


if [[ "$1" == "upload" ]]; then
  aws s3 sync . $bucket/
fi
