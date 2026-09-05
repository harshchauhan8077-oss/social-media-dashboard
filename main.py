import argparse

import analytics
import etl


def main() -> None:
    parser = argparse.ArgumentParser(description="Social Media Engagement Dashboard")
    parser.add_argument(
        "command", choices=["sync", "analyze"],
        help="'sync' fetches latest data, 'analyze' runs engagement analysis",
    )
    args = parser.parse_args()

    if args.command == "sync":
        etl.run()
    else:
        analytics.run()


if __name__ == "__main__":
    main() 