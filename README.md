# HATS cloudtests

[![Template](https://img.shields.io/badge/Template-LINCC%20Frameworks%20Python%20Project%20Template-brightgreen)](https://lincc-ppt.readthedocs.io/en/latest/)

[![GitHub Workflow Status](https://img.shields.io/github/actions/workflow/status/astronomy-commons/hats-cloudtests/smoke-test.yml)](https://github.com/astronomy-commons/hats-cloudtests/actions/workflows/smoke-test.yml)
[![benchmarks](https://img.shields.io/github/actions/workflow/status/astronomy-commons/hats-cloudtests/asv-main.yml?label=benchmarks)](https://astronomy-commons.github.io/hats-cloudtests/)

Integration tests for cloud read and write through HATS and LSDB libraries.

## Why have this repo?

We have abstracted our entire i/o infrastructure to be read through the python 
[fsspec](https://filesystem-spec.readthedocs.io/en/latest/index.html) library, 
using [universal_pathlib](https://github.com/fsspec/universal_pathlib).
All that needs to be provided is a valid protocol pathway, and storage options 
for the cloud interface.

Despite the best efforts of everyone, there are nuances to different file systems.
This repo reflects our own attempts to confirm that we're not introducing regressions
in the HATS and LSDB code bases against continued support for various file systems.

## Dev Guide - Getting Started

Pretty easy, really.

```bash
./setup_dev.sh
```

## Performing HATS cloud tests locally

You'll notice that attempting `>> pytest` on its own doesn't work! 
You must specify the `cloud` you're targeting with tests, as fixtures will be 
different for each test. Some are pretty straightforward, but some require
additional steps, documented here.

### 'local_s3'

A local AWS S3 bucket is created in the `s3_server` pytest fixture. 

This requires NO additional setup, and runs all read and write tests. 
If you're looking for a quick test of some functionality, this is a good place
to start.

### 'http'

A local HTTP server is instantianted via the `http_server` pytest fixture.

This requires NO additional setup, but ONLY runs read tests.

### 'local_gcs'

This test requires a local GCS server running at port 4443. 
The `fake-gcs-server` runs on docker, and so should be instantiated outside
the pytest context.

You can do so with some lines like (on linux):

```bash 
sudo snap install docker
sudo docker pull fsouza/fake-gcs-server
sudo docker run -d -p 4443:4443 --name fake-gcs-server -v ${PWD}/tests/cloud:/data fsouza/fake-gcs-server -scheme http -public-host 0.0.0.0:4443 -external-url http://localhost:4443
```

### 'abfs'

ABFS tests run against production resources on the Microsoft Azure bucket. 
In order to run the tests, you will need to (ask someone for the real values)
and export the following environment variables in a command line:

```bash
export ABFS_LINCCDATA_ACCOUNT_NAME=lincc_account_name
export ABFS_LINCCDATA_ACCOUNT_KEY=lincc_account_key
```

This is currently disabled because the external bucket doesn't exist anymore.

## Contributing

[![GitHub issue custom search in repo](https://img.shields.io/github/issues-search/astronomy-commons/hats-cloudtests?color=purple&label=Good%20first%20issues&query=is%3Aopen%20label%3A%22good%20first%20issue%22)](https://github.com/astronomy-commons/hats-cloudtests/issues?q=is%3Aissue+is%3Aopen+label%3A%22good+first+issue%22)

See the [hats contribution guide](https://hats.readthedocs.io/en/latest/guide/contributing.html)
for contribution best practices.

## Acknowledgements

This project is supported by Schmidt Sciences.

This project is based upon work supported by the National Science Foundation
under Grant No. AST-2003196.

This project acknowledges support from the DIRAC Institute in the Department of 
Astronomy at the University of Washington. The DIRAC Institute is supported 
through generous gifts from the Charles and Lisa Simonyi Fund for Arts and 
Sciences, and the Washington Research Foundation.
