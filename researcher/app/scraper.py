from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]

if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from researcher.app.cli import main as cli_main


def main() -> None:
    sys.argv = ["applyr", "run"]
    cli_main()


if __name__ == "__main__":
    main()
