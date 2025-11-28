from app.models.raw_metrics import RawMetric
from typing import set

def check_cardinality(
    db: Session,
    metric_name: str,
    labels: dict,
    limit: int = None
) -> bool:
    if not labels:
        return True

    distinct_label_sets = (
        db.query(RawMetric.labels)
        .filter(RawMetric.metric_name == metric_name)
        .distinct()
        .all()
    )

    existing_combinations = set()
    for (label_dict,) in distinct_label_sets:    
        label_items = frozenset(label_dict.items())
        existing_combinations.add(label_items)

    new_label_items = frozenset(labels.items())

    if new_label_items not in existing_combinations:
        if limit is not None and len(existing_combinations) >= limit:
            return False

    return True
