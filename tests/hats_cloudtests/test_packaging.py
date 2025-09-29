import hats_cloudtests


def test_version():
    """Check to see that we can get the package version"""
    assert hats_cloudtests.__version__ is not None
