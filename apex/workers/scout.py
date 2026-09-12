"""Scout worker entrypoint — `python -m apex.workers.scout`.

Runs a Celery worker bound to the `scout` queue, consuming tasks from
`apex.workers.tasks.scout_tasks`. This wraps the existing Celery task
surface (preferred over inventing a second agent loop) so compose commands
resolve to real modules.
"""
from __future__ import annotations

import os
import sys


QUEUE = "scout"
HOSTNAME = "scout@%h"
DEFAULT_CONCURRENCY = "5"


def main(argv: list[str] | None = None) -> None:
    from apex.workers.celery_app import celery_app

    concurrency = os.getenv("WORKER_CONCURRENCY", DEFAULT_CONCURRENCY)
    args = argv if argv is not None else [
        "worker",
        f"--hostname={HOSTNAME}",
        f"--queues={QUEUE}",
        f"--concurrency={concurrency}",
        "--loglevel=info",
    ]
    celery_app.worker_main(argv=args)


if __name__ == "__main__":
    main(sys.argv[1:] or None)
