import lsdb
import pandas as pd
import pytest


@pytest.mark.write_to_cloud
def test_save_catalog(local_data_dir, tmp_cloud_path):
    lancedb = pytest.importorskip("lancedb")

    pathway = local_data_dir / "xmatch" / "xmatch_catalog_raw.csv"
    input_df = pd.read_csv(pathway)
    catalog = lsdb.from_dataframe(
        input_df, margin_threshold=5000, catalog_name="small_sky_from_dataframe", catalog_type="object"
    )

    base_catalog_path = tmp_cloud_path / "lance_test"

    storage_options = {}
    if base_catalog_path.protocol == "s3":
        storage_options["aws_endpoint"] = base_catalog_path.storage_options["client_kwargs"]["endpoint_url"]
        storage_options["aws_allow_http"] = "true"

    catalog.to_lance(base_catalog_path=base_catalog_path)

    db = lancedb.connect(str(base_catalog_path), storage_options=storage_options)
    tbl = db.open_table("data")

    lance_df = tbl.to_pandas()
    lance_catalog = lsdb.from_dataframe(
        lance_df, margin_threshold=5000, catalog_name="small_sky_from_dataframe", catalog_type="object"
    )

    assert lance_catalog.hc_structure.catalog_name == catalog.hc_structure.catalog_name
    assert lance_catalog.get_healpix_pixels() == catalog.get_healpix_pixels()
    pd.testing.assert_frame_equal(lance_catalog.compute(), catalog.compute())
