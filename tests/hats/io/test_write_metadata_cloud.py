"""Tests of file IO (reads and writes)"""

import hats.pixel_math as hist
import numpy.testing as npt
import pyarrow as pa
import pyarrow.parquet as pq
import pytest
from hats.io import file_io
from hats.io.parquet_metadata import write_parquet_metadata


@pytest.mark.write_to_cloud
def test_write_parquet_metadata(tmp_cloud_path, small_sky_dir_cloud):
    """Use existing catalog parquet files and create new metadata files for it"""

    basic_catalog_parquet_metadata = pa.schema(
        [
            pa.field("_healpix_29", pa.int64()),
            pa.field("id", pa.int64()),
            pa.field("ra", pa.float64()),
            pa.field("dec", pa.float64()),
            pa.field("ra_error", pa.int64()),
            pa.field("dec_error", pa.int64()),
        ]
    )

    catalog_base_dir = tmp_cloud_path
    dataset_dir = catalog_base_dir / "dataset"

    write_parquet_metadata(catalog_path=small_sky_dir_cloud, output_path=catalog_base_dir)

    check_parquet_schema(dataset_dir / "_metadata", basic_catalog_parquet_metadata)
    ## _common_metadata has 0 row groups
    check_parquet_schema(dataset_dir / "_common_metadata", basic_catalog_parquet_metadata, 0)

    ## Re-write - should still have the same properties.
    write_parquet_metadata(catalog_path=small_sky_dir_cloud, output_path=catalog_base_dir)
    check_parquet_schema(dataset_dir / "_metadata", basic_catalog_parquet_metadata)
    ## _common_metadata has 0 row groups
    check_parquet_schema(dataset_dir / "_common_metadata", basic_catalog_parquet_metadata, 0)


def check_parquet_schema(file_path, expected_schema, expected_num_row_groups=1):
    """Check parquet schema against expectations"""
    assert file_io.does_file_or_directory_exist(file_path)

    single_metadata = file_io.read_parquet_metadata(file_path)
    schema = single_metadata.schema.to_arrow_schema()

    assert len(schema) == len(
        expected_schema
    ), f"object list not the same size ({len(schema)} vs {len(expected_schema)})"

    npt.assert_array_equal(schema.names, expected_schema.names)

    assert schema.equals(expected_schema, check_metadata=False)

    parquet_file = pq.ParquetFile(file_path.path, filesystem=file_path.fs)
    assert parquet_file.metadata.num_row_groups == expected_num_row_groups

    for row_index in range(0, parquet_file.metadata.num_row_groups):
        row_md = parquet_file.metadata.row_group(row_index)
        for column_index in range(0, row_md.num_columns):
            column_metadata = row_md.column(column_index)
            assert column_metadata.file_path.endswith(".parquet")


@pytest.mark.write_to_cloud
def test_read_write_fits_point_map(tmp_cloud_path):
    """Check that we write and can read a FITS file for spatial distribution."""
    initial_histogram = hist.empty_histogram(1)
    filled_pixels = [51, 29, 51, 0]
    initial_histogram[44:] = filled_pixels[:]
    output_file = tmp_cloud_path / "point_map.fits"

    file_io.write_fits_image(initial_histogram, output_file)

    output = file_io.read_fits_image(output_file)
    npt.assert_array_equal(output, initial_histogram)
