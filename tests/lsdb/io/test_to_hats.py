import lsdb
import pandas as pd
import pytest


@pytest.mark.write_to_cloud
def test_save_catalog_and_margin(local_data_dir, tmp_cloud_path):
    pathway = local_data_dir / "xmatch" / "xmatch_catalog_raw.csv"
    input_df = pd.read_csv(pathway)
    catalog = lsdb.from_dataframe(
        input_df, margin_threshold=5000, catalog_name="small_sky_from_dataframe", catalog_type="object"
    )

    base_catalog_path = tmp_cloud_path / "new_catalog_name"
    catalog.to_hats(base_catalog_path)
    expected_catalog = lsdb.read_hats(base_catalog_path)
    assert expected_catalog.hc_structure.catalog_name == catalog.hc_structure.catalog_name
    assert expected_catalog.get_healpix_pixels() == catalog.get_healpix_pixels()
    pd.testing.assert_frame_equal(expected_catalog.compute(), catalog._ddf.compute())

    # When saving a catalog with to_hats, we update the hats_max_rows
    # to the maximum count of points per partition. In this case there
    # is only one with 111 rows, so that is the value we expect.
    original_info = catalog.hc_structure.catalog_info
    partition_sizes = catalog._ddf.map_partitions(len).compute()
    assert max(partition_sizes) == 111
    assert expected_catalog.hc_structure.catalog_info == original_info.copy_and_update(hats_max_rows="111")

    base_catalog_path = tmp_cloud_path / "new_margin_name"
    catalog.margin.to_hats(base_catalog_path)
    expected_catalog = lsdb.read_hats(base_catalog_path)
    assert expected_catalog.hc_structure.catalog_name == catalog.margin.hc_structure.catalog_name
    assert expected_catalog.get_healpix_pixels() == catalog.margin.get_healpix_pixels()
    pd.testing.assert_frame_equal(expected_catalog.compute(), catalog.margin._ddf.compute())

    # Same as above, but now for margin.
    margin_original_info = catalog.margin.hc_structure.catalog_info
    partition_sizes = catalog.margin._ddf.map_partitions(len).compute()
    assert max(partition_sizes) == 3
    assert expected_catalog.hc_structure.catalog_info == margin_original_info.copy_and_update(hats_max_rows="3")
