from hats_import.file_io import (
    directory_has_contents,
    find_files_matching_path,
)


def test_find_files_matching_path(small_sky_dir_cloud):
    ## no_wildcard
    assert len(find_files_matching_path(small_sky_dir_cloud, "properties")) == 1

    ## wilcard in the name, matches properties, partition_info, point_map.fits
    assert len(find_files_matching_path(small_sky_dir_cloud, "p*")) == 3


def test_find_files_matching_path_directory(small_sky_order1_dir_cloud):
    assert len(find_files_matching_path(small_sky_order1_dir_cloud)) == 1

    ## wildcard in directory - will match all files at INDICATED depth
    assert len(find_files_matching_path(small_sky_order1_dir_cloud, "*", "*", "*", "*")) == 15


def test_directory_has_contents(small_sky_order1_dir_cloud):
    assert directory_has_contents(small_sky_order1_dir_cloud)
