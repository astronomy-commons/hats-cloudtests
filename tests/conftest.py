import os
import shlex
import subprocess
import time
from pathlib import Path

import fsspec
import hats as hc
import lsdb
import pytest
import shortuuid
from hats.io.file_io import file_io
from upath import UPath

from hats_cloudtests.temp_cloud_directory import TempCloudDirectory

SMALL_SKY_XMATCH_NAME = "small_sky_xmatch"
XMATCH_CORRECT_FILE = "xmatch_correct.csv"

SMALL_SKY_DIR_NAME = "small_sky"
SMALL_SKY_ORDER1_DIR_NAME = "small_sky_order1"


TEST_DIR = os.path.dirname(__file__)
SMALL_SKY_DIR_NAME = "small_sky"

ALL_CLOUDS = ["abfs", "local_s3", "local_gcs", "http"]
READ_ONLY_CLOUDS = ["local_gcs", "http"]


def pytest_addoption(parser):
    parser.addoption("--cloud", action="store", choices=ALL_CLOUDS)


@pytest.fixture(scope="session", name="cloud")
def cloud(request):
    return request.config.getoption("--cloud")


@pytest.fixture(scope="session", name="http_server")
def http_server(cloud, local_cloud_data_dir):
    if cloud != "http":
        yield None
        return

    requests = pytest.importorskip("requests")
    # pylint: disable=consider-using-with
    proc = subprocess.Popen(
        shlex.split(f"python -m http.server -d {local_cloud_data_dir}"),
        stderr=subprocess.DEVNULL,
        stdout=subprocess.DEVNULL,
    )
    endpoint_uri = "http://0.0.0.0:8000/"
    try:
        timeout = 5
        while timeout > 0:
            try:
                r = requests.get(endpoint_uri, timeout=10)
                if r.ok:
                    break
            except Exception:  # pylint: disable=broad-except
                pass
            timeout -= 0.1
            time.sleep(0.1)
        yield endpoint_uri
    finally:
        proc.terminate()
        proc.wait()


@pytest.fixture(scope="session", name="s3_server")
def s3_server(cloud):
    if cloud != "local_s3":
        yield {}
        return
    # writable local S3 system
    os.environ["BOTO_CONFIG"] = "/dev/null"
    os.environ["AWS_ACCESS_KEY_ID"] = "testing"
    os.environ["AWS_SECRET_ACCESS_KEY"] = "testing"
    os.environ["AWS_SECURITY_TOKEN"] = "testing"
    os.environ["AWS_SESSION_TOKEN"] = "testing"
    os.environ["AWS_DEFAULT_REGION"] = "us-east-1"
    requests = pytest.importorskip("requests")

    pytest.importorskip("moto")

    port = 5555
    endpoint_uri = f"http://127.0.0.1:{port}/"
    # pylint: disable=consider-using-with
    proc = subprocess.Popen(
        shlex.split(f"moto_server -p {port}"),
        stderr=subprocess.DEVNULL,
        stdout=subprocess.DEVNULL,
    )
    try:
        timeout = 5
        while timeout > 0:
            try:
                r = requests.get(endpoint_uri, timeout=10)
                if r.ok:
                    break
            except Exception:  # pylint: disable=broad-except
                pass
            timeout -= 0.1
            time.sleep(0.1)
        s3so = {
            "client_kwargs": {"endpoint_url": endpoint_uri},
            "use_listings_cache": True,
            "anon": False,
        }
        yield s3so
    finally:
        proc.terminate()
        proc.wait()


@pytest.fixture(scope="session", name="cloud_path")
def cloud_path(cloud, s3_server, local_cloud_data_dir, http_server):
    if cloud == "abfs":
        storage_options = {
            "account_name": os.environ.get("ABFS_LINCCDATA_ACCOUNT_NAME"),
            "account_key": os.environ.get("ABFS_LINCCDATA_ACCOUNT_KEY"),
        }

        root_dir = UPath("abfs://hipscat/pytests/", protocol="abfs", **storage_options)
        assert root_dir.exists()
        return root_dir

    if cloud == "local_s3":
        s3so = s3_server
        s3 = fsspec.filesystem("s3", **s3so)
        bucket_name = "test_bucket"
        s3.mkdir(bucket_name)
        for x in Path(local_cloud_data_dir).glob("**/*"):
            target_path = f"{bucket_name}/{x.relative_to(local_cloud_data_dir)}"
            if x.is_file():
                s3.upload(str(x), target_path)
        s3.invalidate_cache()
        root_dir = UPath(f"{bucket_name}", protocol="s3", **s3so)
        assert root_dir.exists()
        return root_dir

    if cloud == "http":
        root_dir = UPath(http_server)
        assert root_dir.exists()
        return root_dir

    if cloud == "local_gcs":
        root_dir = UPath(
            "gcs://",
            protocol="gcs",
            endpoint_url="http://0.0.0.0:4443",
            token="anon",
        )
        assert root_dir.exists()
        raw_dir = root_dir / "raw"
        raw_dir.fs.invalidate_cache()
        assert raw_dir.exists()
        return root_dir

    raise NotImplementedError("Cloud format not implemented for tests!")


@pytest.fixture(scope="session", name="storage_options")
def storage_options(cloud, s3_server):
    if cloud == "abfs":
        storage_options = {
            "account_name": os.environ.get("ABFS_LINCCDATA_ACCOUNT_NAME"),
            "account_key": os.environ.get("ABFS_LINCCDATA_ACCOUNT_KEY"),
        }
        return storage_options
    if cloud == "local_s3":
        s3so = s3_server
        s3so["protocol"] = "s3"
        return s3so
    if cloud == "local_gcs":
        storage_options = {"protocol": "gcs", "endpoint_url": "http://0.0.0.0:4443", "token": "anon"}
        return storage_options

    return {}


def pytest_collection_modifyitems(session, items):
    """Add SKIP directive to tests that will write to cloud IF running
    tests against a read-only file system (e.g. HTTP)"""
    cloud = session.config.getoption("--cloud")
    if not cloud:
        pytest.exit(f"FAIL: --cloud option is required (options: {ALL_CLOUDS})")
    if cloud not in ALL_CLOUDS:
        pytest.exit(f"FAIL: Unsupported cloud type: {cloud}")
    if cloud in READ_ONLY_CLOUDS:
        skip_write = pytest.mark.skip(reason="Skipping write tests for read-only file system.")
        skip_range = pytest.mark.skip(reason="Skipping index tests for non-range reads.")
        for item in items:
            for _ in item.iter_markers(name="write_to_cloud"):
                item.add_marker(skip_write)
            for _ in item.iter_markers(name="requires_range"):
                item.add_marker(skip_range)


@pytest.fixture(scope="session", name="tmp_dir_cloud")
def tmp_dir_cloud(cloud_path, cloud):
    """Create a single client for use by all unit test cases."""
    ## Read-only filesystem
    if cloud in READ_ONLY_CLOUDS:
        yield None
        return

    real_directories = True
    if cloud in ("local_s3"):
        real_directories = False
    tmp = TempCloudDirectory(
        cloud_path / "tmp",
        method_name="full_test",
        real_directories=real_directories,
    )
    yield tmp.open()
    tmp.close()


@pytest.fixture
def tmp_cloud_path(request, tmp_dir_cloud):
    name = request.node.name
    my_uuid = shortuuid.uuid()
    # Strip out the "test_" at the beginning of each method name, make it a little
    # shorter, and add a disambuating UUID.
    return tmp_dir_cloud / f"{name[5:25]}_{my_uuid}"


##   --------------------------------------------------------------------------
##                      Just boring path stuff after this point
##   --------------------------------------------------------------------------


@pytest.fixture(scope="session")
def local_cloud_data_dir():
    local_data_path = os.path.dirname(__file__)
    return Path(local_data_path) / "cloud"


@pytest.fixture
def local_data_dir():
    local_data_path = os.path.dirname(__file__)
    return Path(local_data_path) / "data"


@pytest.fixture
def small_sky_dir_local(local_data_dir):
    return local_data_dir / SMALL_SKY_DIR_NAME


@pytest.fixture
def small_sky_order1_dir_local(local_data_dir):
    return local_data_dir / SMALL_SKY_ORDER1_DIR_NAME


@pytest.fixture
def small_sky_parts_dir_local(local_data_dir):
    return local_data_dir / "small_sky_parts"


@pytest.fixture
def test_data_dir_cloud(cloud_path):
    return cloud_path / "data"


@pytest.fixture
def small_sky_dir_cloud(cloud_path):
    return cloud_path / "data" / SMALL_SKY_DIR_NAME


@pytest.fixture
def small_sky_order1_dir_cloud(cloud_path):
    return cloud_path / "data" / SMALL_SKY_ORDER1_DIR_NAME


@pytest.fixture
def small_sky_order1_catalog_dir_cloud(small_sky_order1_dir_cloud):
    return small_sky_order1_dir_cloud / "small_sky_order1"


@pytest.fixture
def small_sky_index_dir_cloud(small_sky_order1_dir_cloud):
    return small_sky_order1_dir_cloud / "small_sky_object_index"


@pytest.fixture
def small_sky_margin_dir_cloud(small_sky_order1_dir_cloud):
    return small_sky_order1_dir_cloud / "small_sky_order1_margin"


@pytest.fixture
def small_sky_xmatch_dir_cloud(cloud_path):
    return cloud_path / "data" / SMALL_SKY_XMATCH_NAME


@pytest.fixture
def small_sky_catalog_cloud(small_sky_dir_cloud):
    return lsdb.read_hats(small_sky_dir_cloud)


@pytest.fixture
def small_sky_xmatch_catalog_cloud(small_sky_xmatch_dir_cloud):
    return lsdb.read_hats(small_sky_xmatch_dir_cloud)


@pytest.fixture
def small_sky_order1_hats_catalog_cloud(small_sky_order1_catalog_dir_cloud):
    return hc.read_hats(small_sky_order1_catalog_dir_cloud)


@pytest.fixture
def small_sky_order1_catalog_cloud(small_sky_order1_dir_cloud):
    return lsdb.read_hats(small_sky_order1_dir_cloud)


@pytest.fixture
def small_sky_npix_as_dir_cloud(cloud_path):
    return cloud_path / "data" / "small_sky_npix_as_dir"


@pytest.fixture
def xmatch_correct_cloud(local_data_dir):
    pathway = local_data_dir / "xmatch" / XMATCH_CORRECT_FILE
    return file_io.load_csv_to_pandas(pathway)


@pytest.fixture
def xmatch_with_margin(local_data_dir):
    pathway = local_data_dir / "xmatch" / "xmatch_with_margin.csv"
    return file_io.load_csv_to_pandas(pathway)


class Helpers:
    """Helper methods for comparing catalogs"""

    # pylint: disable=too-few-public-methods
    @staticmethod
    def assert_catalog_info_is_correct(expected_catalog_info, catalog_info, **properties_to_update):
        """Check that the catalog properties are similar to the expected ones."""
        do_not_compare = {prop: None for prop in ["hats_creation_date", "hats_estsize"]}
        expected_catalog_info = expected_catalog_info.copy_and_update(**do_not_compare)
        catalog_info = catalog_info.copy_and_update(**(properties_to_update | do_not_compare))
        assert expected_catalog_info == catalog_info


@pytest.fixture
def helpers():
    return Helpers()
