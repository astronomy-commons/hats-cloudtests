import pytest


@pytest.mark.requires_range
def test_index_search(small_sky_order1_catalog_cloud, small_sky_index_dir_cloud):
    index_search_catalog = small_sky_order1_catalog_cloud.id_search(
        values={"id": 900}, index_catalogs={"id": small_sky_index_dir_cloud}
    )
    index_search_df = index_search_catalog.compute()
    assert len(index_search_df) == 0

    index_search_catalog = small_sky_order1_catalog_cloud.id_search(
        values={"id": 700}, index_catalogs={"id": small_sky_index_dir_cloud}
    )
    index_search_df = index_search_catalog.compute()
    assert len(index_search_df) == 1
