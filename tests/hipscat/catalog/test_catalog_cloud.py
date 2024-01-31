"""Tests of catalog functionality"""

import os

import pytest
from hipscat.catalog import Catalog, PartitionInfo
from hipscat.io.file_io import file_io
from hipscat.pixel_math import HealpixPixel

from hipscat_cloudtests import TempCloudDirectory


def test_load_catalog_small_sky(small_sky_dir_cloud, example_cloud_storage_options):
    """Instantiate a catalog with 1 pixel"""
    cat = Catalog.read_from_hipscat(small_sky_dir_cloud, storage_options=example_cloud_storage_options)

    assert cat.catalog_name == "small_sky"
    assert len(cat.get_healpix_pixels()) == 1


def test_empty_directory(tmp_dir_cloud, example_cloud_storage_options):
    """Test loading empty or incomplete data"""
    with TempCloudDirectory(tmp_dir_cloud, "empty", example_cloud_storage_options) as temp_path:
        catalog_path = temp_path

        ## Path exists but there's nothing there (which means it doesn't exist!)
        with pytest.raises(FileNotFoundError, match="No directory"):
            Catalog.read_from_hipscat(catalog_path, storage_options=example_cloud_storage_options)

        ## catalog_info file exists - getting closer
        file_name = os.path.join(catalog_path, "catalog_info.json")
        file_io.write_string_to_file(
            file_name,
            string='{"catalog_name":"empty", "catalog_type":"source"}',
            storage_options=example_cloud_storage_options,
        )

        with pytest.raises(FileNotFoundError, match="metadata"):
            Catalog.read_from_hipscat(catalog_path, storage_options=example_cloud_storage_options)

        ## partition_info file exists - enough to create a catalog
        ## Now we create the needed _metadata and everything is right.
        part_info = PartitionInfo.from_healpix([HealpixPixel(0, 11)])
        part_info.write_to_metadata_files(
            catalog_path=catalog_path, storage_options=example_cloud_storage_options
        )

        catalog = Catalog.read_from_hipscat(catalog_path, storage_options=example_cloud_storage_options)
        assert catalog.catalog_name == "empty"