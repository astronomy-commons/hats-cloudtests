from hats.io.file_io import (
    directory_has_contents,
    does_file_or_directory_exist,
    find_files_matching_path,
    is_regular_file,
)


def test_file_or_dir_exist(small_sky_dir_cloud):
    assert does_file_or_directory_exist(small_sky_dir_cloud / "properties")


def test_is_regular_file(small_sky_dir_cloud):
    partition_info_file = small_sky_dir_cloud / "properties"
    assert is_regular_file(partition_info_file)

    assert not is_regular_file(small_sky_dir_cloud)

    partition_dir = small_sky_dir_cloud / "Norder=0"
    assert not is_regular_file(partition_dir)


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
