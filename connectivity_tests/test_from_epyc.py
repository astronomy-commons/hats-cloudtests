import lsdb.nested as nd
import numpy as np
import pandas as pd


def test_from_epyc():
    """test a dataset from epyc. Motivated by https://github.com/lincc-frameworks/nested-dask/issues/21"""
    # Load some ZTF data
    catalogs_dir = "https://epyc.astro.washington.edu/~lincc-frameworks/half_degree_surveys/ztf/"

    object_ndf = (
        nd.read_parquet(f"{catalogs_dir}/ztf_object", columns=["ra", "dec", "ps1_objid"])
        .set_index("ps1_objid", sort=True)
        .persist()
    )

    source_ndf = (
        nd.read_parquet(
            f"{catalogs_dir}/ztf_source", columns=["mjd", "mag", "magerr", "band", "ps1_objid", "catflags"]
        )
        .set_index("ps1_objid", sort=True)
        .persist()
    )

    object_ndf = object_ndf.join_nested(source_ndf, "ztf_source")

    # Apply a mean function
    meta = pd.DataFrame(columns=[0], dtype=float)
    result = object_ndf.map_rows(
        np.mean, columns=["ztf_source.mag"], row_container="args", meta=meta
    ).compute()

    # just make sure the result was successfully computed
    assert len(result) == 9817
