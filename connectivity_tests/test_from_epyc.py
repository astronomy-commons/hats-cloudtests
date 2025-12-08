import hats.io.file_io as file_io
import numpy as np


def test_from_epyc():
    """test a dataset from epyc. Motivated by https://github.com/lincc-frameworks/nested-dask/issues/21"""
    # Load some ZTF data
    catalogs_dir = "https://epyc.astro.washington.edu/~lincc-frameworks/half_degree_surveys/ztf/"

    object_ndf = file_io.read_parquet_file_to_pandas(
        f"{catalogs_dir}/ztf_object/Norder=3/Dir=0/Npix=433.parquet", columns=["ra", "dec", "ps1_objid"]
    ).set_index("ps1_objid")

    source_ndf = file_io.read_parquet_file_to_pandas(
        f"{catalogs_dir}/ztf_source/Norder=6/Dir=20000/Npix=27754.parquet",
        columns=["mjd", "mag", "magerr", "band", "ps1_objid", "catflags"],
    ).set_index("ps1_objid")

    object_ndf = object_ndf.join_nested(source_ndf, "ztf_source")

    # Apply a mean function
    result = object_ndf.map_rows(np.mean, columns=["ztf_source.mag"], row_container="args")

    # just make sure the result was successfully computed
    assert len(result) == 1086
