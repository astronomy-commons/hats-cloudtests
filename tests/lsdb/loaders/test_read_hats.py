import lsdb
from hats.pixel_math import HealpixPixel
from lsdb.catalog.margin_catalog import MarginCatalog


def test_read_hats(small_sky_order1_dir_cloud, small_sky_order1_hats_catalog_cloud):
    catalog = lsdb.read_hats(small_sky_order1_dir_cloud)
    assert isinstance(catalog, lsdb.Catalog)
    assert catalog.hc_structure.catalog_base_dir == small_sky_order1_hats_catalog_cloud.catalog_base_dir
    assert catalog.get_healpix_pixels() == small_sky_order1_hats_catalog_cloud.get_healpix_pixels()

    for healpix_pixel in small_sky_order1_hats_catalog_cloud.get_healpix_pixels():
        catalog.get_partition(healpix_pixel.order, healpix_pixel.pixel)


def test_read_hats_margin(small_sky_margin_dir_cloud):
    catalog = lsdb.read_hats(small_sky_margin_dir_cloud)
    assert isinstance(catalog, MarginCatalog)
    assert catalog.hc_structure.catalog_base_dir == small_sky_margin_dir_cloud
    assert catalog.get_healpix_pixels() == [
        HealpixPixel(0, 4),
        HealpixPixel(1, 44),
        HealpixPixel(1, 45),
        HealpixPixel(1, 46),
        HealpixPixel(1, 47),
    ]
