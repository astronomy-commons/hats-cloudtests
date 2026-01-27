import pytest
from hats_import.catalog.file_readers import (
    CsvPyarrowReader,
    CsvReader,
    FitsReader,
    IndexedCsvReader,
    IndexedParquetReader,
    ParquetPandasReader,
    ParquetPyarrowReader,
)


@pytest.fixture
def local_indexed_files(cloud, local_data_dir):
    return local_data_dir / f"indexed_files_{cloud}"


@pytest.fixture
def raw_data_dir(cloud_path):
    return cloud_path / "raw"


def test_indexed_parquet_reader(storage_options, local_indexed_files):
    # Chunksize covers all the inputs.
    total_chunks = 0
    total_len = 0
    for frame in IndexedParquetReader(chunksize=10_000, upath_kwargs=storage_options).read(
        local_indexed_files / "parquet_list_single.txt"
    ):
        total_chunks += 1
        assert len(frame) == 131
        total_len += len(frame)

    assert total_chunks == 1
    assert total_len == 131

    # Requesting a very small chunksize. This will split up reads on the parquet.
    total_chunks = 0
    total_len = 0
    for frame in IndexedParquetReader(chunksize=5, upath_kwargs=storage_options).read(
        local_indexed_files / "parquet_list_single.txt"
    ):
        total_chunks += 1
        assert len(frame) <= 5
        total_len += len(frame)

    assert total_chunks == 28
    assert total_len == 131


def test_indexed_csv_reader(storage_options, local_indexed_files):
    # Chunksize covers all the inputs.
    total_chunks = 0
    total_len = 0
    for frame in IndexedCsvReader(chunksize=10_000, upath_kwargs=storage_options).read(
        local_indexed_files / "csv_list_single.txt"
    ):
        total_chunks += 1
        assert len(frame) == 131
        total_len += len(frame)

    assert total_chunks == 1
    assert total_len == 131

    # Requesting a very small chunksize. This will split up reads on the parquet.
    total_chunks = 0
    total_len = 0
    for frame in IndexedCsvReader(chunksize=5, upath_kwargs=storage_options).read(
        local_indexed_files / "csv_list_single.txt"
    ):
        total_chunks += 1
        assert len(frame) <= 5
        total_len += len(frame)

    assert total_chunks == 29
    assert total_len == 131


def test_read_fits(raw_data_dir):
    """Success case - fits file that exists being read as fits"""
    total_chunks = 0
    for frame in FitsReader().read(raw_data_dir / "small_sky.fits"):
        total_chunks += 1
        assert len(frame) == 131

    assert total_chunks == 1


def test_csv_readers(raw_data_dir):
    """Verify we can read the csv file into a single data frame."""
    total_chunks = 0
    for frame in CsvReader(compression="gzip").read(raw_data_dir / "catalog.csv.gz"):
        total_chunks += 1
        assert len(frame) == 131

    assert total_chunks == 1


def test_csv_pyarrow_reader(raw_data_dir):
    """Verify we can read the csv file into a single data frame."""
    total_chunks = 0
    total_chunks = 0
    for frame in CsvPyarrowReader(compression="gzip").read(raw_data_dir / "catalog.csv.gz"):
        total_chunks += 1
        assert len(frame) == 131

    assert total_chunks == 1


def test_parquet_reader_pandas(small_sky_dir_cloud):
    """Verify we can read the csv file into a single data frame."""
    single_parquet = small_sky_dir_cloud / "dataset" / "Norder=0" / "Dir=0" / "Npix=11.parquet"
    total_chunks = 0
    for frame in ParquetPandasReader().read(single_parquet):
        total_chunks += 1
        assert len(frame) == 131

    assert total_chunks == 1


def test_parquet_reader_pyarrow(small_sky_dir_cloud):
    """Verify we can read the csv file into a single data frame."""
    single_parquet = small_sky_dir_cloud / "dataset" / "Norder=0" / "Dir=0" / "Npix=11.parquet"
    total_chunks = 0
    for frame in ParquetPyarrowReader().read(single_parquet):
        total_chunks += 1
        assert len(frame) == 131

    assert total_chunks == 1
