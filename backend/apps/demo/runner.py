from __future__ import annotations

import logging
import os
import random
import sys
import threading
import time

from django.conf import settings

from apps.demo.activity import get_demo_activity_config, run_demo_activity_once

logger = logging.getLogger(__name__)

SERVER_COMMAND_KEYWORDS = ("runserver", "daphne", "uvicorn", "gunicorn")

_runner_started = False
_runner_lock = threading.Lock()

ERROR_BACKOFF_SECONDS = 5


def _is_server_command() -> bool:
    argv = " ".join(sys.argv).lower()
    return any(keyword in argv for keyword in SERVER_COMMAND_KEYWORDS)


def should_start_demo_runner() -> bool:
    if not settings.DEMO_ACTIVITY_ENABLED:
        return False

    run_main = os.environ.get("RUN_MAIN")
    if run_main is not None and run_main != "true":
        return False

    if not _is_server_command():
        return False

    return True


def _demo_activity_loop() -> None:
    config = get_demo_activity_config()
    time.sleep(config.startup_delay_seconds)

    while True:
        try:
            result = run_demo_activity_once()
            if result["generated_count"]:
                logger.info(
                    "Demo activity batch complete: %s message(s) in conversations %s",
                    result["generated_count"],
                    result["conversation_ids"],
                )
            elif result["skipped_reason"]:
                logger.debug("Demo activity batch skipped: %s", result["skipped_reason"])

            interval = random.uniform(
                config.min_interval_seconds,
                config.max_interval_seconds,
            )
            time.sleep(interval)
        except Exception:
            logger.exception("Demo activity runner error")
            time.sleep(ERROR_BACKOFF_SECONDS)


def start_demo_activity_runner() -> None:
    global _runner_started

    if not should_start_demo_runner():
        return

    with _runner_lock:
        if _runner_started:
            return
        _runner_started = True

    thread = threading.Thread(
        target=_demo_activity_loop,
        name="demo-activity",
        daemon=True,
    )
    thread.start()
    logger.info("Demo activity runner started.")
