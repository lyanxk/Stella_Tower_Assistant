from __future__ import annotations

import argparse

from .api.app import create_app
from .core.automation.run_loop import run_automation
from .core.config.settings import API_HOST, API_PORT


def main() -> None:
    parser = argparse.ArgumentParser(prog="stella-tower")
    subparsers = parser.add_subparsers(dest="command")

    subparsers.add_parser("run", help="Run the automation loop directly")

    serve_parser = subparsers.add_parser("serve", help="Serve the local automation API")
    serve_parser.add_argument("--host", default=API_HOST)
    serve_parser.add_argument("--port", type=int, default=API_PORT)

    args = parser.parse_args()

    if args.command in (None, "run"):
        run_automation()
        return

    if args.command == "serve":
        import uvicorn

        uvicorn.run(create_app(), host=args.host, port=args.port)


if __name__ == "__main__":
    main()
