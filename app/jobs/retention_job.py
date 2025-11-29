import asyncio
import logging 
from datetime import datetime 
from app.db import SessionLocal
from app.services.retention_service import RetentionService


logging.basicConfig(level=logging.INFO,format="%(asctime)s - %(levelname)s - %(message)s")

logger=logging.getLogger(__name__)


async def run_retention_job():
    db=SessionLocal()
    try:
        logger.info("Starting retention job")
        start_time=datetime.now()
        retention_service=RetentionService(db)
        results=await retention_service.apply_retention_policies()
        execution_time=(datetime.now()-start_time).total_seconds()
        logger.info(
            f"Retention job completed in {execution_time:.2f}s: "
            f"Deleted {results['raw']} raw metrics, "
            f"Deleted {results['1m']} '1m' rollup metrics, "
            f"Deleted {results['5m']} '5m' rollup metrics, "
            f"Deleted {results['1h']} '1h' rollup metrics."
        )

    except Exception as e:
        logger.error(f"Error during retention job: {str(e)}", exc_info=True)

    finally:
        db.close()


async def run_continuous():
    logger.info(
        f"Starting continuous retention job"
        f"(interval: 24 hours)"
    )
    while True:
        try:
            await run_retention_job()
        except Exception as e:
            logger.error(f"Error in continuous retention job: {str(e)}", exc_info=True)
        await asyncio.sleep(24 * 60 * 60)


if __name__=="__main__":
    asyncio.run(run_continuous())