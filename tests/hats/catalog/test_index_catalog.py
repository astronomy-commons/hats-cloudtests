import numpy.testing as npt
import pytest
from hats.catalog.index.index_catalog import IndexCatalog
from hats.loaders import read_hats
from hats.pixel_math import HealpixPixel


@pytest.mark.requires_range
def test_loc_partition(small_sky_index_dir_cloud):
    catalog = read_hats(small_sky_index_dir_cloud)

    assert isinstance(catalog, IndexCatalog)
    assert catalog.on_disk
    assert catalog.catalog_path == small_sky_index_dir_cloud

    npt.assert_array_equal(catalog.loc_partitions([700]), [HealpixPixel(1, 46)])
    npt.assert_array_equal(catalog.loc_partitions([707]), [HealpixPixel(1, 44)])
    npt.assert_array_equal(catalog.loc_partitions([900]), [])
