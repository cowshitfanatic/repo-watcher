import argparse
import logging
from .rat import ReleaseRat

def main() -> None:
    parser = argparse.ArgumentParser(description="Watch GitHub releases and report worthwhile changes.")
    parser.add_argument("--once", action="store_true", help="Run one polling cycle and exit.")
    parser.add_argument("--dry-run", action="store_true", help="Do not persist state or notify.")
    parser.add_argument("--config", default="config.yaml")
    parser.add_argument("--state", default="data/state.json")
    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    rat = ReleaseRat(args.config, args.state)
    if args.once or args.dry_run:
        results = rat.run_once(dry_run=args.dry_run)
        for release, assessment in results:
            print(f"{release.repository} {release.tag_name}: {assessment.summary}")
    else:
        rat.watch()
