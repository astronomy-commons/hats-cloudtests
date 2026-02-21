import nested_pandas as npd
import numpy as np
import pandas as pd
import pytest
from hats.io import paths
from hats.io.file_io import (
    directory_has_contents,
    load_csv_to_pandas,
    load_csv_to_pandas_generator,
    load_text_file,
    read_fits_image,
    read_parquet_dataset,
    read_parquet_file_to_pandas,
    write_dataframe_to_csv,
    write_fits_image,
    write_string_to_file,
)
from hats.io.paths import pixel_catalog_file, pixel_directory
from hats.pixel_math.healpix_pixel import HealpixPixel
from upath import UPath


@pytest.mark.write_to_cloud
def test_write_string_to_file(tmp_cloud_path):
    test_file_path = tmp_cloud_path / "text_file.txt"
    test_string = "this is a test"
    write_string_to_file(test_file_path, test_string, encoding="utf-8")
    data = load_text_file(test_file_path, encoding="utf-8")
    assert data[0] == test_string


def test_read_parquet_to_pandas(small_sky_dir_local, small_sky_dir_cloud):
    target_pixel = HealpixPixel(0, 11)
    pixel_data_path = pixel_catalog_file(small_sky_dir_local, target_pixel)
    parquet_df = npd.read_parquet(pixel_data_path, partitioning=None)

    pixel_data_path_cloud = pixel_catalog_file(small_sky_dir_cloud, target_pixel)
    loaded_df = read_parquet_file_to_pandas(pixel_data_path_cloud)
    pd.testing.assert_frame_equal(parquet_df, loaded_df)

    pixel_data_path_cloud = pixel_directory(small_sky_dir_cloud, target_pixel.order, target_pixel.pixel)
    loaded_df = read_parquet_file_to_pandas(pixel_data_path_cloud)
    pd.testing.assert_frame_equal(parquet_df, loaded_df)


def test_read_parquet_to_pandas_dir(small_sky_dir_local, small_sky_order1_catalog_dir_cloud):
    # Read a directory of data into a single frame. This is the same content as the full version.
    pixel_data_path = pixel_catalog_file(small_sky_dir_local, HealpixPixel(0, 11))
    parquet_df = npd.read_parquet(pixel_data_path, partitioning=None)

    pixel_data_path_cloud = small_sky_order1_catalog_dir_cloud / "dataset" / "Norder=1" / "Dir=0"
    loaded_df = read_parquet_file_to_pandas(pixel_data_path_cloud)
    assert len(loaded_df) == len(parquet_df)
    loaded_df = loaded_df.sort_values("_healpix_29").reset_index(drop=True)
    pd.testing.assert_frame_equal(parquet_df, loaded_df)


@pytest.mark.write_to_cloud
def test_write_df_to_csv(tmp_cloud_path):
    random_df = pd.DataFrame(np.random.randint(0, 100, size=(100, 4)), columns=list("ABCD"))
    test_file_path = tmp_cloud_path / "test.csv"
    write_dataframe_to_csv(random_df, test_file_path, index=False)
    loaded_df = load_csv_to_pandas(test_file_path)
    pd.testing.assert_frame_equal(loaded_df, random_df)


@pytest.mark.write_to_cloud
def test_load_csv_to_pandas_generator_encoding(tmp_cloud_path):
    path = tmp_cloud_path / "koi8-r.csv"
    with path.open(encoding="koi8-r", mode="w") as fh:
        fh.write("col1,col2\nыыы,яяя\n")
    num_reads = 0
    for frame in load_csv_to_pandas_generator(path, chunksize=7, encoding="koi8-r"):
        assert len(frame) == 1
        num_reads += 1
    assert num_reads == 1


@pytest.mark.write_to_cloud
def test_write_point_map_roundtrip(small_sky_dir_cloud, tmp_cloud_path):
    """Test the reading/writing of a catalog point map"""
    expected_counts_skymap = read_fits_image(paths.get_point_map_file_pointer(small_sky_dir_cloud))
    output_map_pointer = paths.get_point_map_file_pointer(tmp_cloud_path)
    write_fits_image(expected_counts_skymap, output_map_pointer)
    counts_skymap = read_fits_image(output_map_pointer)
    np.testing.assert_array_equal(counts_skymap, expected_counts_skymap)


def test_read_parquet_dataset(small_sky_dir_cloud, cloud, storage_options, local_data_dir):
    # We're going to add some spice in here. If the protocol SHOULD be stripped
    ## from the path for reading via pyarrow parquet dataset, confirm that the
    ## returned string paths do not have this protocol prefix. At current,
    ## protocol stripping is understood for S3 and GCS.

    protocol_prefix = None
    if cloud == "local_s3":
        protocol_prefix = "s3"
    if cloud == "local_gcs":
        protocol_prefix = "gcs"

    # Single file.
    paths, ds = read_parquet_dataset(
        small_sky_dir_cloud / "dataset" / "Norder=0" / "Dir=0" / "Npix=11.parquet"
    )

    assert ds.count_rows() == 131

    if protocol_prefix:
        assert not paths.startswith(protocol_prefix)

    # Single file, but passed as a list.
    paths, ds = read_parquet_dataset(
        [small_sky_dir_cloud / "dataset" / "Norder=0" / "Dir=0" / "Npix=11.parquet"]
    )

    assert ds.count_rows() == 131
    if protocol_prefix:
        assert not paths[0].startswith(protocol_prefix)

    # Multiple files. Load them with the appropriate storage options, since they're just strings right now.
    file_names = load_text_file(local_data_dir / f"indexed_files_{cloud}" / "parquet_list_single.txt")
    file_names = [UPath(f.strip(), **storage_options) for f in file_names]

    paths, ds = read_parquet_dataset(file_names)

    assert ds.count_rows() == 131
    if protocol_prefix:
        assert np.all([not path.startswith(protocol_prefix) for path in paths])


def test_directory_has_contents(small_sky_order1_dir_cloud):
    assert directory_has_contents(small_sky_order1_dir_cloud)
