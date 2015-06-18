
from ahem.utils import celery_is_available


if not celery_is_available():
    print("ATTENTION: Running Ahem tests without Celery")
