"""Functional tests for catalog import"""

import hats_import.catalog.run_import as runner
import pytest
from hats import read_hats
from hats_import.catalog.arguments import ImportArguments
from hats_import.catalog.file_readers import CsvReader

from hats_cloudtests import assert_parquet_file_ids


@pytest.mark.write_to_cloud
@pytest.mark.dask
def test_catalog_import_write_to_cloud(
    dask_client,
    small_sky_parts_dir_local,
    tmp_cloud_path,
    tmp_path,
):
    """Using local CSV files, write a new catalog to the cloud bucket."""
    args = ImportArguments(
        output_artifact_name="small_sky_object_catalog",
        input_path=small_sky_parts_dir_local,
        file_reader="csv",
        output_path=tmp_cloud_path,
        dask_tmp=tmp_path,
        highest_healpix_order=1,
        progress_bar=False,
    )

    runner.run(args, dask_client)

    # Check that the catalog metadata file exists
    catalog = read_hats(args.catalog_path)
    assert catalog.on_disk
    assert catalog.catalog_path == args.catalog_path
    assert catalog.catalog_info.ra_column == "ra"
    assert catalog.catalog_info.dec_column == "dec"
    assert catalog.catalog_info.total_rows == 131
    assert len(catalog.get_healpix_pixels()) == 1

    # Check that the catalog parquet file exists and contains correct object IDs
    output_file = args.catalog_path / "dataset" / "Norder=0" / "Dir=0" / "Npix=11.parquet"

    expected_ids = list(range(700, 831))
    assert_parquet_file_ids(output_file, "id", catalog.schema, expected_ids)


@pytest.mark.dask
def test_catalog_import_read_from_cloud(dask_client, small_sky_parts_dir_cloud, tmp_path):
    """Using cloud CSV files, write a new catalog to local disk."""
    args = ImportArguments(
        output_artifact_name="small_sky_object_catalog",
        input_path=small_sky_parts_dir_cloud,
        file_reader=CsvReader(),
        output_path=tmp_path,
        dask_tmp=tmp_path,
        highest_healpix_order=1,
        progress_bar=False,
    )

    runner.run(args, dask_client)

    # Check that the catalog metadata file exists
    catalog = read_hats(args.catalog_path)
    assert catalog.on_disk
    assert catalog.catalog_path == args.catalog_path
    assert catalog.catalog_info.ra_column == "ra"
    assert catalog.catalog_info.dec_column == "dec"
    assert catalog.catalog_info.total_rows == 131
    assert len(catalog.get_healpix_pixels()) == 1

    # Check that the catalog parquet file exists and contains correct object IDs
    output_file = args.catalog_path / "dataset" / "Norder=0" / "Dir=0" / "Npix=11.parquet"

    expected_ids = [*range(700, 831)]
    assert_parquet_file_ids(output_file, "id", catalog.schema, expected_ids)


def test_read_csv_cloud(small_sky_parts_dir_cloud):
    """Verify we can read the csv file into a single data frame."""
    single_file = small_sky_parts_dir_cloud / "catalog_00_of_05.csv"
    total_chunks = 0
    for frame in CsvReader().read(single_file):
        total_chunks += 1
        assert len(frame) == 25

    assert total_chunks == 1


def test_no_import_overwrite(small_sky_order1_dir_cloud, small_sky_parts_dir_local):
    """Runner should refuse to overwrite a valid catalog"""
    catalog_dir = small_sky_order1_dir_cloud.parent
    catalog_name = small_sky_order1_dir_cloud.name
    with pytest.raises(ValueError, match="already contains a valid catalog"):
        ImportArguments(
            input_path=small_sky_parts_dir_local,
            output_path=catalog_dir,
            output_artifact_name=catalog_name,
            file_reader="parquet",
        )
