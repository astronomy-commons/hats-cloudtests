import lsdb


def test_from_vizcat():
    gaia = lsdb.open_catalog(
        "https://vizcat.cds.unistra.fr/hats:n=10000/gaia_dr3/",
        columns=["DR3Name", "RA_ICRS", "DE_ICRS"],
    )
    head_frame = gaia.head(10)
    assert len(head_frame) == 10
