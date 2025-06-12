import lsdb
import numpy as np
import numpy.testing as npt
import pandas as pd
import pytest
from hats.io.file_io import read_fits_image


@pytest.mark.write_to_cloud
def test_save_catalog(local_data_dir, tmp_cloud_path):
    pathway = local_data_dir / "xmatch" / "xmatch_catalog_raw.csv"
    input_df = pd.read_csv(pathway)
    catalog = lsdb.from_dataframe(
        input_df, margin_threshold=5000, catalog_name="small_sky_from_dataframe", catalog_type="object"
    )

    base_catalog_path = tmp_cloud_path / "new_catalog_name"
    catalog.to_hats(
        base_catalog_path, skymap_alt_orders=[1, 2], addl_hats_properties={"obs_regime": "Optical"}
    )
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
    assert expected_catalog.hc_structure.catalog_info == original_info.copy_and_update(
        hats_max_rows="111",
        skymap_order=8,
        skymap_alt_orders=[1, 2],
        obs_regime="Optical",
    )

    assert (base_catalog_path / "properties").exists()
    assert (base_catalog_path / "hats.properties").exists()

    point_map_path = base_catalog_path / "point_map.fits"
    assert point_map_path.exists()
    histogram = read_fits_image(point_map_path)

    skymap_path = base_catalog_path / "skymap.fits"
    assert skymap_path.exists()
    skymap_histogram = read_fits_image(skymap_path)

    # The histogram and the sky map histogram match
    assert len(catalog) == np.sum(skymap_histogram)
    npt.assert_array_equal(histogram, skymap_histogram)

    skymap_path = base_catalog_path / "skymap.1.fits"
    assert skymap_path.exists()

    skymap_path = base_catalog_path / "skymap.2.fits"
    assert skymap_path.exists()

    new_catalog = lsdb.open_catalog(base_catalog_path)
    assert new_catalog.hc_structure.catalog_info.skymap_alt_orders == [1, 2]
    assert new_catalog.hc_structure.catalog_info.skymap_order == 8
