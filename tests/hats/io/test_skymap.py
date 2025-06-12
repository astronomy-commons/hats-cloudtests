import hats.pixel_math.healpix_shim as hp
import numpy as np
import pytest
from hats.io.file_io import read_fits_image
from hats.io.skymap import write_skymap


@pytest.mark.write_to_cloud
def test_write_sampled_skymaps_roundtrip(tmp_cloud_path):
    """Test the reading/writing of a catalog point map"""
    dense = np.arange(0, 3072)
    assert sum(dense) == 4_717_056
    orders = [1, 2]

    write_skymap(dense, tmp_cloud_path, orders)
    skymap_path = tmp_cloud_path / "skymap.fits"
    assert skymap_path.exists()
    counts_skymap = read_fits_image(tmp_cloud_path / "skymap.fits")
    np.testing.assert_array_equal(counts_skymap, dense)

    for order in range(0, 5):
        skymap_atorder_path = tmp_cloud_path / f"skymap.{order}.fits"
        if order in orders:
            assert skymap_atorder_path.exists()
            read_histogram = read_fits_image(skymap_atorder_path)
            assert hp.npix2order(len(read_histogram)) == order
            # Check that the contents have same overall count, and we're summing quadratically.
            assert sum(read_histogram) == 4_717_056
            pixel_size = 4 ** (4 - order)
            assert read_histogram[-1] == sum(dense[-1 * pixel_size :])
        else:
            assert not skymap_atorder_path.exists()
