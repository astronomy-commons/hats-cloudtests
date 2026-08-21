import pytest
from dask.distributed import Client


@pytest.fixture(scope="session", name="dask_client")
def dask_client():
    """Create a single client for use by all unit test cases."""
    client = Client()
    yield client
    try:
        client.close()
    except RuntimeError as e:
        if "Cannot synchronously wait on a running event loop" in str(e):
            # Silently ignore event loop conflicts during test cleanup
            pass
        else:
            raise

@pytest.fixture
def small_sky_parts_dir_cloud(cloud_path):
    return cloud_path / "raw" / "small_sky_parts"
