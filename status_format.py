import argparse
import json


def do_thing(input_file, output_file, prefix, repo_name):
    with open(input_file, "r", encoding="utf-8") as json_file:
        full_json = json.load(json_file)

    to_report = {}

    for job in full_json["jobs"]:
        if job["name"].startswith(prefix) and job["conclusion"].startswith("fail"):
            to_report[job["name"]] = job

    table_rows = [[{"type": "raw_text", "text": "job name"}, {"type": "raw_text", "text": "workflow URL"}]]
    for key in sorted(to_report):
        print(key, to_report[key]["conclusion"], to_report[key]["run_id"])
        url = f"https://github.com/astronomy-commons/hats-cloudtests/actions/runs/{to_report[key]["run_id"]}/job/{to_report[key]["id"]}"

        row = [{"type": "raw_text", "text": key}, {"type": "rich_text", "elements": [
							{
								"type": "rich_text_section",
								"elements": [
									{
										"text": url,
										"type": "link",
										"url": url
									}
								]
							}
						]}]
        table_rows.append(row)
    payload = {
        "blocks": [
            {
                "type": "header",
                "text": {"type": "plain_text", "text": f"Smoke Test Failures {repo_name }"},
            },
            {"type": "table", "rows": table_rows},
        ]
    }

    dumped_metadata = json.dumps(payload, indent=4)
    with open(output_file, "w") as f:
        f.write(dumped_metadata + "\n")


def main():
    """Main entry point for the script."""
    parser = argparse.ArgumentParser(description="Matrix workflow conclusion formatter")
    parser.add_argument("input_file", type=str, help="Input JSON file, with all workflow job statuses")
    parser.add_argument(
        "output_file", type=str, help="Output JSON file, ready to be a slack api message payload"
    )
    parser.add_argument("--prefix", type=str, default="build", help="Base name of the job to report on")
    parser.add_argument("--repo_name", type=str, default="", help="Name for repository: Used in message.")
    args = parser.parse_args()

    do_thing(args.input_file, args.output_file, args.prefix, args.repo_name)

    return


if __name__ == "__main__":
    main()
