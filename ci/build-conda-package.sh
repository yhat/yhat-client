#!/bin/bash

set -ex

bucket="yhat-conda-channel"
mkdir "${bucket}"
cd "${bucket}"

bucket="s3://$bucket/linux-64"

pkg="yhat==1.9.0"
pkgname=$(python -c "print '$pkg'.split('==')[0]")
pkgversion=$(python -c "print '$pkg'.split('==')[1]")
echo "building $pkg $pkgname $pkgversion"

aws s3 sync $bucket/.index.json .
aws s3 sync $bucket/repodata.json .
aws s3 sync $bucket/repodata.json.bz2 .
pip install $pkg
conda package --pkg-name "$pkgname" --pkg-version "$pkgversion"
conda index --no-remove
# aws s3 sync --acl-public . $bucket/
tree .
