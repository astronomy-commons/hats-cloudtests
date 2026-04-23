import lsdb


def test_from_huggingface():
    vipers = lsdb.open_catalog(
        "hf://datasets/LSDB/mmu_vipers_w1",
        columns=["spectrum.mask", "REDSHIFT", "object_id", "ra", "dec"],
    )
    head_frame = vipers.partitions[0].head(10)
    assert head_frame.shape == (10, 5)
    assert head_frame.nested_columns == ["spectrum"]
    assert head_frame["spectrum.mask"].min() == 0
