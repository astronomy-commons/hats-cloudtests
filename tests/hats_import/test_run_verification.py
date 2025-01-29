import hats_import.verification.run_verification as runner
import pandas as pd
from hats_import.verification.arguments import VerificationArguments


def test_runner(small_sky_dir_cloud, tmp_path):
    """Runner should execute all tests and write a report to file."""
    result_cols = ["datetime", "passed", "test", "target"]

    args = VerificationArguments(input_catalog_path=small_sky_dir_cloud, output_path=tmp_path)
    verifier = runner.run(args, write_mode="w")
    all_passed = verifier.results_df.passed.all()
    assert all_passed, "good catalog failed"
    written_results = pd.read_csv(args.output_path / args.output_filename, comment="#")
    assert written_results[result_cols].equals(verifier.results_df[result_cols]), "report failed"
