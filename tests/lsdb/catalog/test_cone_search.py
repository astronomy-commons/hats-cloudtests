from astropy.coordinates import SkyCoord


def test_cone_search_filters_correct_points(small_sky_order1_catalog_cloud):
    ra = 0
    dec = -80
    radius_degrees = 20
    radius = radius_degrees * 3600
    center_coord = SkyCoord(ra, dec, unit="deg")
    cone_search_catalog = small_sky_order1_catalog_cloud.cone_search(ra, dec, radius).compute()
    for _, row in small_sky_order1_catalog_cloud.compute().iterrows():
        row_ra = row[small_sky_order1_catalog_cloud.hc_structure.catalog_info.ra_column]
        row_dec = row[small_sky_order1_catalog_cloud.hc_structure.catalog_info.dec_column]
        sep = SkyCoord(row_ra, row_dec, unit="deg").separation(center_coord)
        if sep.degree <= radius_degrees:
            assert len(cone_search_catalog.loc[cone_search_catalog["id"] == row["id"]]) == 1
        else:
            assert len(cone_search_catalog.loc[cone_search_catalog["id"] == row["id"]]) == 0


def test_cone_search_filters_partitions(small_sky_order1_catalog_cloud):
    ra = 0
    dec = -80
    radius_degrees = 20
    radius = radius_degrees * 3600
    hc_conesearch = small_sky_order1_catalog_cloud.hc_structure.filter_by_cone(ra, dec, radius)
    consearch_catalog = small_sky_order1_catalog_cloud.cone_search(ra, dec, radius)
    assert len(hc_conesearch.get_healpix_pixels()) == len(consearch_catalog.get_healpix_pixels())
    assert len(hc_conesearch.get_healpix_pixels()) == consearch_catalog.npartitions
    for pixel in hc_conesearch.get_healpix_pixels():
        assert pixel in consearch_catalog.get_healpix_pixels()
