"""
run.py - HR Data Automation Suite Orchestrator
================================================
Entry point for the automation system.
Do not modify this file unless you are a developer.

User workflow:
  1. Place SAP export files in the correct INPUT subfolder
  2. Double-click RUN_ME.bat
  3. Collect results from OUTPUT folder
"""
import json
import sys
import time
from pathlib import Path

from src.logger import setup_logger
from src.summary import write_summary
import src.cost_center      as mod_cost_center
import src.join_date        as mod_join_date
import src.position_tenure  as mod_position_tenure

CONFIG_FILE = Path("config/settings.json")


def load_settings() -> dict:
    """Load settings.json; return safe defaults if file is missing."""
    if not CONFIG_FILE.exists():
        return {
            "run_modules": {
                "cost_center":     True,
                "join_date":       True,
                "position_tenure": True,
            }
        }
    with open(CONFIG_FILE, "r", encoding="utf-8-sig") as f:
        return json.load(f)


def main():
    start = time.time()
    logger   = setup_logger("logs")
    settings = load_settings()
    modules  = settings.get("run_modules", {})

    logger.info("=" * 60)
    logger.info("  HR DATA AUTOMATION SUITE")
    logger.info("=" * 60)

    results = []

    if modules.get("cost_center", True):
        logger.info("-" * 40)
        logger.info("  MODULE 1: General Cost Center")
        logger.info("-" * 40)
        results.append(mod_cost_center.run(logger))

    if modules.get("join_date", True):
        logger.info("-" * 40)
        logger.info("  MODULE 2: Join Date & Years of Service")
        logger.info("-" * 40)
        results.append(mod_join_date.run(logger))

    if modules.get("position_tenure", True):
        logger.info("-" * 40)
        logger.info("  MODULE 3: Position Effective Date & Current Tenure")
        logger.info("-" * 40)
        results.append(mod_position_tenure.run(logger))

    logger.info("-" * 40)
    write_summary(results, logger)

    elapsed = time.time() - start
    success = all(r.get("Status") == "SUCCESS" for r in results)
    label   = "ALL MODULES COMPLETED SUCCESSFULLY" if success else "COMPLETED WITH ERRORS â€” check LOGS"

    logger.info("=" * 60)
    logger.info(f"  {label}")
    logger.info(f"  Total elapsed time: {elapsed:.1f}s")
    logger.info("=" * 60)

    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
