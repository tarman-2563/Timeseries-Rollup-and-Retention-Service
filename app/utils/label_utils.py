from app.models.raw_metrics import RawMetrics
from sqlalchemy.orm import Session
from typing import Optional, Dict
import hashlib
import json


def check_cardinality(
    db: Session,
    metric_name: str,
    labels: dict,
    limit: int = None
) -> bool:
    if not labels:
        return True

    distinct_label_sets = (
        db.query(RawMetrics.labels)
        .filter(RawMetrics.metric_name == metric_name)
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

def normalize_labels(labels:Optional[Dict[str,str]])->Dict[str,str]:
    if not labels:
        return {}
    return dict(sorted(labels.items()))

def hash_labels(labels:Optional[Dict[str,str]])->str:
    normalized=normalize_labels(labels)
    labels_str=json.dumps(normalized,sort_keys=True)
    return hashlib.md5(labels_str.encode()).hexdigest()

