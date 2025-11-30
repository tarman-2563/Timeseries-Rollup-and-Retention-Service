from sqlalchemy import text
from app.db import engine

def fix_schema():
    with engine.connect() as conn:

        conn.execute(text("""
            ALTER TABLE raw_metrics
            DROP COLUMN IF EXISTS metric_value;
        """))

        conn.execute(text("""
            ALTER TABLE raw_metrics
            ADD COLUMN IF NOT EXISTS value DOUBLE PRECISION;
        """))
        conn.execute(text("""
            ALTER TABLE raw_metrics
            ADD COLUMN IF NOT EXISTS tenant_id VARCHAR;
        """))
        conn.execute(text("""
            ALTER TABLE raw_metrics
            ADD COLUMN IF NOT EXISTS labels JSON;
        """))
        conn.execute(text("""
            ALTER TABLE raw_metrics
            ADD COLUMN IF NOT EXISTS created_at TIMESTAMP DEFAULT NOW();
        """))

        conn.commit()
