"""
run.py — HR Data Automation Suite Orchestrator
================================================
Entry point for the automation system.

Executes all 6 business modules + Final Assembler:
  1. Contract Type & Contract End Date
  2. Education, Institute & Branch of Study
  3. Entity, Division, Area, Function
  4. General Cost Center & Description
  5. Join Date & Years of Service
  6. Position Effective Date & Current Tenure
  7. Final Topic Report Assembler
"""
import json
import sys
import time
from pathlib import Path

from src.logger import setup_logger
from src.summary import write_summary

import src.contract_type    as mod_contract_type
import src.education        as mod_education
import src.entity_division  as mod_entity_division
import src.cost_center      as mod_cost_center
import src.join_date        as mod_join_date
import src.position_tenure  as mod_position_tenure
import src.assembler        as mod_assembler

CONFIG_FILE = Path("config/settings.json")


def load_settings() -> dict:
    """Load settings.json; return safe defaults if file is missing."""
    if not CONFIG_FILE.exists():
        return {
            "run_modules": {
                "contract_type":    True,
                "education":        True,
                "entity_division":  True,
                "cost_center":      True,
                "join_date":        True,
                "position_tenure":  True,
                "assembler":        True,
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
    logger.info("  HR DATA AUTOMATION SUITE — FULL TOPIC REPORT")
    logger.info("=" * 60)

    results = []

    # 1. Partner Modules
    if modules.get("contract_type", True):
        logger.info("-" * 40)
        logger.info("  MODULE 1: Contract Type & End Date")
        logger.info("-" * 40)
        results.append(mod_contract_type.run(logger))

    if modules.get("education", True):
        logger.info("-" * 40)
        logger.info("  MODULE 2: Education, Institute & Branch")
        logger.info("-" * 40)
        results.append(mod_education.run(logger))

    if modules.get("entity_division", True):
        logger.info("-" * 40)
        logger.info("  MODULE 3: Entity, Division, Area, Function")
        logger.info("-" * 40)
        results.append(mod_entity_division.run(logger))

    # 2. Existing Modules
    if modules.get("cost_center", True):
        logger.info("-" * 40)
        logger.info("  MODULE 4: General Cost Center")
        logger.info("-" * 40)
        results.append(mod_cost_center.run(logger))

    if modules.get("join_date", True):
        logger.info("-" * 40)
        logger.info("  MODULE 5: Join Date & Years of Service")
        logger.info("-" * 40)
        results.append(mod_join_date.run(logger))

    if modules.get("position_tenure", True):
        logger.info("-" * 40)
        logger.info("  MODULE 6: Position Effective Date & Current Tenure")
        logger.info("-" * 40)
        results.append(mod_position_tenure.run(logger))

    # 3. Final Assembler
    if modules.get("assembler", True):
        logger.info("-" * 40)
        logger.info("  FINAL STEP: Assembling Topic Report")
        logger.info("-" * 40)
        results.append(mod_assembler.run(logger))

    logger.info("-" * 40)
    write_summary(results, logger)

    elapsed = time.time() - start
    success = all(r.get("Status") == "SUCCESS" for r in results)
    label   = "ALL MODULES COMPLETED SUCCESSFULLY" if success else "COMPLETED WITH WARNINGS/ERRORS — check LOGS"

    logger.info("=" * 60)
    logger.info(f"  {label}")
    logger.info(f"  Total elapsed time: {elapsed:.1f}s")
    logger.info("=" * 60)

    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
