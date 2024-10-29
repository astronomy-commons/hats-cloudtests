"""Tests of catalog functionality"""

from hats.catalog import Catalog
from hats.io.validation import is_valid_catalog
from hats.loaders import read_hats


def test_load_catalog_small_sky_with_loader(small_sky_dir_cloud):
    """Instantiate a catalog with 1 pixel"""
    cat = read_hats(small_sky_dir_cloud)

    assert isinstance(cat, Catalog)
    assert cat.catalog_name == "small_sky"
    assert len(cat.get_healpix_pixels()) == 1

    assert is_valid_catalog(small_sky_dir_cloud)
