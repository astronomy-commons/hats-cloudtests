import hats_import.soap.run_soap as runner
import pytest
from hats import read_hats
from hats.io.file_io import read_parquet_metadata
from hats_import.soap.arguments import SoapArguments


@pytest.mark.dask
def test_object_to_self_write_to_cloud(
    dask_client,
    tmp_path_factory,
    tmp_cloud_path,
    small_sky_dir_local,
    small_sky_order1_dir_local,
):
    """Test creating association between object catalogs.

    using:
    - local origin catalogs
    - writing to CLOUD

    First test creates leaf files, the second test does not (exercies different write calls).
    """
    small_sky_soap_args = SoapArguments(
        object_catalog_dir=small_sky_dir_local,
        object_id_column="id",
        source_catalog_dir=small_sky_order1_dir_local,
        source_object_id_column="id",
        source_id_column="id",
        write_leaf_files=True,
        output_artifact_name="small_sky_to_order1",
        output_path=tmp_cloud_path,
        progress_bar=False,
        tmp_dir=tmp_path_factory.mktemp("small_sky_order_to_order1"),
    )
    runner.run(small_sky_soap_args, dask_client)

    ## Check that the association data can be parsed as a valid association catalog.
    catalog = read_hats(small_sky_soap_args.catalog_path)
    assert catalog.on_disk
    assert catalog.catalog_path == small_sky_soap_args.catalog_path
    assert len(catalog.get_join_pixels()) == 4
    assert catalog.catalog_info.total_rows == 131
    assert catalog.catalog_info.contains_leaf_files

    parquet_file_name = (
        small_sky_soap_args.catalog_path / "dataset" / "Norder=0" / "Dir=0" / "Npix=11.parquet"
    )
    parquet_file_metadata = read_parquet_metadata(parquet_file_name)
    assert parquet_file_metadata.num_row_groups == 4
    assert parquet_file_metadata.num_rows == 131
    assert parquet_file_metadata.num_columns == 8

    small_sky_soap_args = SoapArguments(
        object_catalog_dir=small_sky_dir_local,
        object_id_column="id",
        source_catalog_dir=small_sky_order1_dir_local,
        source_object_id_column="id",
        source_id_column="id",
        write_leaf_files=False,
        output_artifact_name="small_sky_to_order1_soft",
        output_path=tmp_cloud_path,
        progress_bar=False,
        tmp_dir=tmp_path_factory.mktemp("small_sky_to_order1_soft"),
    )
    runner.run(small_sky_soap_args, dask_client)

    ## Check that the association data can be parsed as a valid association catalog.
    catalog = read_hats(small_sky_soap_args.catalog_path)
    assert catalog.on_disk
    assert catalog.catalog_path == small_sky_soap_args.catalog_path
    assert len(catalog.get_join_pixels()) == 4
    assert catalog.catalog_info.total_rows == 131
    assert not catalog.catalog_info.contains_leaf_files


@pytest.mark.dask
def test_object_to_self_read_from_cloud(
    dask_client, tmp_path, small_sky_dir_cloud, small_sky_order1_dir_cloud
):
    """Test creating association between object catalogs.

    using:
    - CLOUD origin catalogs
    - writing to local tmp

    First test creates leaf files, the second test does not (exercies different write calls).
    """
    small_sky_soap_args = SoapArguments(
        object_catalog_dir=small_sky_dir_cloud,
        object_id_column="id",
        source_catalog_dir=small_sky_order1_dir_cloud,
        source_object_id_column="id",
        source_id_column="id",
        write_leaf_files=True,
        output_artifact_name="small_sky_to_order1",
        output_path=tmp_path,
        progress_bar=False,
        tmp_dir=tmp_path,
    )
    runner.run(small_sky_soap_args, dask_client)

    ## Check that the association data can be parsed as a valid association catalog.
    catalog = read_hats(small_sky_soap_args.catalog_path)
    assert catalog.on_disk
    assert catalog.catalog_path == small_sky_soap_args.catalog_path
    assert len(catalog.get_join_pixels()) == 4
    assert catalog.catalog_info.total_rows == 131
    assert catalog.catalog_info.contains_leaf_files

    parquet_file_name = (
        small_sky_soap_args.catalog_path / "dataset" / "Norder=0" / "Dir=0" / "Npix=11.parquet"
    )
    parquet_file_metadata = read_parquet_metadata(parquet_file_name)
    assert parquet_file_metadata.num_row_groups == 4
    assert parquet_file_metadata.num_rows == 131
    assert parquet_file_metadata.num_columns == 8
