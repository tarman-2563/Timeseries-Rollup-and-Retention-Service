import asyncio
import logging
import json
import os
from datetime import datetime,timedelta
from pathlib import Path
from app.db import SessionLocal
from app.services.rollup_service import RollupService

logging.basicConfig(level=logging.INFO,format="%(asctime)s - %(levelname)s - %(message)s")
logger=logging.getLogger(__name__)

State_file=Path("rollup_state.json")

def load_last_processed_time()->datetime:
    if State_file.exists():
        try:
            with open(State_file,"r") as f:
                state=json.load(f)
                timestamp_str=state.get("last_processed_time")
                if timestamp_str:
                    return datetime.fromisoformat(timestamp_str)
        except Exception as e:
            logger.error(f"Error loading state file: {e}")

    return datetime.utcnow()-timedelta(hours=1)

def save_last_processed_time(timestamp:datetime):
    try:
        state={
            "last_processed_time":timestamp.isoformat(),
            "last_run":datetime.utcnow().isoformat()
        }
        with open(State_file,"w") as f:
            json.dump(state,f,indent=2)

    except Exception as e:
        logger.error(f"Error saving state file: {e}")

async def run_rollup_job():
    db=SessionLocal()
    try:
        since=load_last_processed_time()
        logger.info(f"Starting rollup job since {since.isoformat()}")
        rollup_service=RollupService(db)
        start_time=datetime.utcnow()
        stats=await rollup_service.perform_rollups(since)
        end_time=datetime.utcnow()

        processing_time=(end_time-start_time).total_seconds()

        logger.info(f"Rollup job completed in {processing_time:.2f}s :"
                   f"Processed {stats['raw_metrics_processed']} raw metrics,"
                   f"Created {stats['rollup_metrics_created']} rollup metrics"
                   f"for windows {stats['windows_processed']}"
        )

        save_last_processed_time(datetime.utcnow())

    except Exception as e:
        logger.error(f"Error during rollup job: {e}")
    finally:
        db.close()


async def run_continuous():
    interval=60
    logger.info(f"Starting continuous rollup job with interval {interval}s")

    while True:
        try:
            await run_rollup_job()
        except Exception as e:
            logger.error(f"Unhandled error in rollup job: {e}",exc_info=True)
        logger.info(f"Waiting {interval}s until next rollup job")

        await asyncio.sleep(interval)

def main():
    logger.info("Starting rollup job main function")
    try:
        asyncio.run(run_continuous())
    except KeyboardInterrupt:
        logger.info("Rollup job interrupted by user, exiting...")
    except Exception as e:
        logger.error(f"Fatal error in rollup job main: {e}",exc_info=True)

if __name__=="__main__":
    main()

