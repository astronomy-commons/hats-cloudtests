import lsdb
import numpy as np
from hats.pixel_math import HealpixPixel
from hats.pixel_math.spatial_index import SPATIAL_INDEX_COLUMN
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
        HealpixPixel(0, 7),
        HealpixPixel(0, 8),
        HealpixPixel(1, 44),
        HealpixPixel(1, 45),
        HealpixPixel(1, 46),
        HealpixPixel(1, 47),
    ]


def test_read_hats_npix_as_dir(small_sky_npix_as_dir_cloud):
    catalog = lsdb.read_hats(small_sky_npix_as_dir_cloud)
    # Show that npix_suffix indicates that Npix are directories and also matches the hats property.
    catalog_npix_suffix = catalog.hc_structure.catalog_info.npix_suffix
    assert catalog_npix_suffix == "/"
    # Show that the catalog can be read as expected.
    assert isinstance(catalog, lsdb.Catalog)
    assert catalog.hc_structure.catalog_info.total_rows == len(catalog)
    assert len(catalog.compute().columns) == 5


def test_read_hats_collection_nested_filters(small_sky_order1_dir_cloud):
    """Tests that we appropriately handled nested pyarrow compute expressions,
    where all clauses are AND'd together"""
    catalog = lsdb.open_catalog(
        small_sky_order1_dir_cloud,
        columns=["ra", "dec"],
        filters=[[("ra", ">", 300), ("dec", "<", -50)]],
    )

    assert isinstance(catalog, lsdb.Catalog)
    assert all(catalog.columns == ["ra", "dec"])
    assert catalog.hc_structure.schema.names == ["ra", "dec", SPATIAL_INDEX_COLUMN]
    catalog_contents = catalog.compute()
    assert np.all(catalog_contents["ra"] > 300)
    assert np.all(catalog_contents["dec"] < -50)

    assert isinstance(catalog.margin, lsdb.MarginCatalog)
    assert all(catalog.margin.columns == ["ra", "dec"])
    assert catalog.margin.hc_structure.schema.names == ["ra", "dec", SPATIAL_INDEX_COLUMN]
    catalog_contents = catalog.margin.compute()
    assert np.all(catalog_contents["ra"] > 300)
    assert np.all(catalog_contents["dec"] < -50)


def test_read_hats_collection_nested_filters_or(small_sky_order1_dir_cloud):
    """Tests that we appropriately handled nested pyarrow compute expressions,
    where clauses are OR'd together"""
    catalog = lsdb.open_catalog(
        small_sky_order1_dir_cloud,
        columns=["ra", "dec"],
        filters=[[("ra", ">", 340)], [("ra", "<", 290)]],
    )

    assert isinstance(catalog, lsdb.Catalog)
    assert all(catalog.columns == ["ra", "dec"])
    assert catalog.hc_structure.schema.names == ["ra", "dec", SPATIAL_INDEX_COLUMN]
    catalog_contents = catalog.compute()
    assert np.all(np.logical_or(catalog_contents["ra"] > 340, catalog_contents["ra"] < 290))

    assert isinstance(catalog.margin, lsdb.MarginCatalog)
    assert all(catalog.margin.columns == ["ra", "dec"])
    assert catalog.margin.hc_structure.schema.names == ["ra", "dec", SPATIAL_INDEX_COLUMN]
    catalog_contents = catalog.margin.compute()
    assert np.all(np.logical_or(catalog_contents["ra"] > 340, catalog_contents["ra"] < 290))


def test_read_hats_collection_empty_filters(small_sky_order1_dir_cloud):
    catalog = lsdb.open_catalog(small_sky_order1_dir_cloud, filters=None)

    assert isinstance(catalog, lsdb.Catalog)
    assert all(catalog.columns == ["id", "ra", "dec", "ra_error", "dec_error"])

    assert isinstance(catalog.margin, lsdb.MarginCatalog)
    assert all(catalog.margin.columns == ["id", "ra", "dec", "ra_error", "dec_error"])

    catalog = lsdb.open_catalog(
        small_sky_order1_dir_cloud / "small_sky_order1",
        margin_cache=small_sky_order1_dir_cloud / "small_sky_order1_margin",
        filters=None,
    )

    assert isinstance(catalog, lsdb.Catalog)
    assert all(catalog.columns == ["id", "ra", "dec", "ra_error", "dec_error"])

    assert isinstance(catalog.margin, lsdb.MarginCatalog)
    assert all(catalog.margin.columns == ["id", "ra", "dec", "ra_error", "dec_error"])
