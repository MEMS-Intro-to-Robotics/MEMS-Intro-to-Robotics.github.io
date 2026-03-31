#!/usr/bin/env python3
"""Runtime utilities for robust gripper command execution."""

import threading
import time
from dataclasses import dataclass


@dataclass(frozen=True)
class GripperRuntimeConfig:
    close_timeout_s: float = 2.5
    open_timeout_s: float = 1.5
    close_settle_s: float = 0.2
    open_settle_s: float = 0.2
    recovery_pause_s: float = 0.1


class GripperCommandRunner:
    """
    Wrap gripper commands with bounded waits and non-fatal recovery.
    This is intended to stay out of student-facing task logic.
    """

    def __init__(self, logger, config: GripperRuntimeConfig | None = None):
        self._logger = logger
        self._config = config or GripperRuntimeConfig()

    def _timeout_for(self, command_name: str) -> float:
        return (
            self._config.close_timeout_s
            if command_name == "close"
            else self._config.open_timeout_s
        )

    def _settle_for(self, command_name: str) -> float:
        return (
            self._config.close_settle_s
            if command_name == "close"
            else self._config.open_settle_s
        )

    def run_command(self, gripper, command_name: str) -> bool:
        if gripper is None:
            self._logger.warn(f"No gripper interface available; skipping '{command_name}'.")
            return False

        if command_name not in ("open", "close"):
            self._logger.warn(f"Unsupported gripper command '{command_name}'.")
            return False

        send_command = gripper.close if command_name == "close" else gripper.open
        timeout_s = self._timeout_for(command_name)
        settle_s = self._settle_for(command_name)

        try:
            send_command()
        except Exception as error:
            self._logger.warn(
                f"Failed to send gripper '{command_name}' command: {error}"
            )
            return False

        result = {"done": False, "ok": False, "error": None}

        def _wait_worker():
            try:
                result["ok"] = bool(gripper.wait_until_executed())
            except Exception as wait_error:
                result["error"] = wait_error
            finally:
                result["done"] = True

        waiter = threading.Thread(target=_wait_worker, daemon=True)
        waiter.start()
        waiter.join(timeout=timeout_s)

        timed_out = not result["done"]
        wait_error = result["error"] is not None
        reported_failure = result["done"] and not result["ok"]

        if timed_out or wait_error or reported_failure:
            if timed_out:
                self._logger.warn(
                    f"Gripper '{command_name}' timed out after {timeout_s:.1f}s; "
                    "resetting state and continuing."
                )
            elif wait_error:
                self._logger.warn(
                    f"Gripper '{command_name}' wait raised an exception; "
                    f"resetting state and continuing: {result['error']}"
                )
            else:
                self._logger.warn(
                    f"Gripper '{command_name}' reported incomplete execution; "
                    "resetting state and continuing."
                )

            try:
                gripper.force_reset_executing_state()
            except Exception as reset_error:
                self._logger.warn(f"Gripper recovery reset failed: {reset_error}")

            time.sleep(self._config.recovery_pause_s)
            if settle_s > 0.0:
                time.sleep(settle_s)
            self._logger.warn(f"Continuing task after gripper '{command_name}' recovery.")
            return False

        if settle_s > 0.0:
            time.sleep(settle_s)
        return True
