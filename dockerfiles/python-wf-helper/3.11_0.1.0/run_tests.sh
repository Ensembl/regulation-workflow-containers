#!/bin/sh

set -uef
set -o xtrace

python - <<'PY'
import boto3
import numpy
import pandas
import pydantic
import requests
import urllib3

assert pydantic.__version__.split(".", 1)[0] == "1"
print(
    f"boto3={boto3.__version__} numpy={numpy.__version__} "
    f"pandas={pandas.__version__} pydantic={pydantic.__version__} "
    f"requests={requests.__version__} urllib3={urllib3.__version__}"
)
PY

python -m pip check
