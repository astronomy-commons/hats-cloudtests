import lsdb


class BenchmarksHTTP:
    """Benchmark LSDB operations via HTTP."""

    timeout = 180
    rounds = 1
    repeat = 2
    number = 1

    def setup(self):
        # pylint: disable=attribute-defined-outside-init
        self.gaia = lsdb.open_catalog(
            "https://data.lsdb.io/hats/gaia_dr3",
            search_filter=lsdb.PixelSearch([(6, 29070)]),
            columns=["source_id", "ra", "dec"],
        )

    def time_gaia(self):
        self.gaia.compute()

    def peakmem_gaia(self):
        self.gaia.compute()


class BenchmarksCDSHTTP:
    """Benchmark LSDB operations via CDS's HTTP."""

    timeout = 480
    rounds = 1
    repeat = 2
    number = 1

    def setup(self):
        # pylint: disable=attribute-defined-outside-init
        self.gaia = lsdb.open_catalog(
            "https://vizcat.cds.unistra.fr/hats:n=1000000/gaia_dr3/",
            search_filter=lsdb.PixelSearch([(7, 114853)]),
            columns=["DR3Name", "RA_ICRS", "DE_ICRS"],
        )

    def time_gaia(self):
        self.gaia.compute()


class BenchmarksS3:
    """Benchmark LSDB operations via S3."""

    timeout = 120
    rounds = 1
    repeat = 2
    number = 1

    def setup(self):
        # pylint: disable=attribute-defined-outside-init
        self.euclid = lsdb.open_catalog(
            "s3://nasa-irsa-euclid-q1/contributed/q1/merged_objects/hats",
            search_filter=lsdb.PixelSearch([(6, 16045)]),
            columns=["object_id", "ra", "dec"],
        )

    def time_euclid(self):
        self.euclid.compute()

    def peakmem_euclid(self):
        self.euclid.compute()
