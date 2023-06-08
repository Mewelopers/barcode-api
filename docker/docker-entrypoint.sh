#!/bin/bash

set -euxo pipefail

pushd /app
make migrate
make start

popd