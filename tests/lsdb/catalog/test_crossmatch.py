import lsdb
import pytest


def test_kdtree_crossmatch(small_sky_catalog_cloud, small_sky_xmatch_catalog_cloud, xmatch_correct_cloud):
    with pytest.warns(RuntimeWarning, match="Results may be incomplete"):
        xmatched = small_sky_catalog_cloud.crossmatch(
            small_sky_xmatch_catalog_cloud, radius_arcsec=0.01 * 3600
        ).compute()
    assert len(xmatched) == len(xmatch_correct_cloud)
    for _, correct_row in xmatch_correct_cloud.iterrows():
        assert correct_row["small_sky_id"] in xmatched["id_small_sky"].to_numpy()
        xmatch_row = xmatched[xmatched["id_small_sky"] == correct_row["small_sky_id"]]
        assert xmatch_row["id_small_sky_xmatch"].to_numpy() == correct_row["xmatch_id"]
        assert xmatch_row["_dist_arcsec"].to_numpy() == pytest.approx(correct_row["dist_arcsec"])


def test_crossmatch_with_margin(
    small_sky_order1_dir_cloud,
    small_sky_xmatch_dir_cloud,
    small_sky_margin_dir_cloud,
    xmatch_with_margin,
):
    small_sky_order1_catalog = lsdb.read_hats(
        small_sky_order1_dir_cloud, margin_cache=small_sky_margin_dir_cloud
    )
    small_sky_xmatch_catalog = lsdb.read_hats(small_sky_xmatch_dir_cloud)
    xmatched = small_sky_xmatch_catalog.crossmatch(
        small_sky_order1_catalog, n_neighbors=3, radius_arcsec=2 * 3600
    ).compute()
    assert len(xmatched) == len(xmatch_with_margin)
    for _, correct_row in xmatch_with_margin.iterrows():
        assert correct_row["small_sky_order1_id"] in xmatched["id_small_sky_order1"].to_numpy()
        xmatch_row = xmatched[
            (xmatched["id_small_sky_order1"] == correct_row["small_sky_order1_id"])
            & (xmatched["id_small_sky_xmatch"] == correct_row["xmatch_id"])
        ]
        assert len(xmatch_row) == 1
        assert xmatch_row["_dist_arcsec"].to_numpy() == pytest.approx(correct_row["dist_arcsec"])
