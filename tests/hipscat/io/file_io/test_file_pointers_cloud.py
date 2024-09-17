from hipscat.io.file_io import (
    directory_has_contents,
    does_file_or_directory_exist,
    find_files_matching_path,
    get_directory_contents,
    is_regular_file,
)


def test_file_or_dir_exist(small_sky_dir_cloud):
    assert does_file_or_directory_exist(small_sky_dir_cloud)


def test_is_regular_file(small_sky_dir_cloud):
    partition_info_file = small_sky_dir_cloud / "catalog_info.json"
    assert is_regular_file(partition_info_file)

    assert not is_regular_file(small_sky_dir_cloud)

    partition_dir = small_sky_dir_cloud / "Norder=0"
    assert not is_regular_file(partition_dir)


def test_find_files_matching_path(small_sky_dir_cloud):
    ## no_wildcard
    assert len(find_files_matching_path(small_sky_dir_cloud, "catalog_info.json")) == 1

    ## wilcard in the name, matches catalog_info.json and provenance_info.json
    assert len(find_files_matching_path(small_sky_dir_cloud, "*.json")) == 2


def test_find_files_matching_path_directory(small_sky_order1_dir_cloud):
    assert len(find_files_matching_path(small_sky_order1_dir_cloud)) == 1

    ## wildcard in directory - will match all files at indicated depth
    assert len(find_files_matching_path(small_sky_order1_dir_cloud, "*", "*", "*")) == 4


def test_directory_has_contents(small_sky_order1_dir_cloud):
    assert directory_has_contents(small_sky_order1_dir_cloud)


def test_get_directory_contents(small_sky_order1_dir_cloud):
    small_sky_contents = get_directory_contents(small_sky_order1_dir_cloud)

    expected = [
        "Norder=1",
        "_common_metadata",
        "_metadata",
        "catalog_info.json",
        "partition_info.csv",
        "point_map.fits",
        "provenance_info.json",
    ]

    expected = [small_sky_order1_dir_cloud / file_name for file_name in expected]

    assert small_sky_contents == expected
