from celery import Celery


from .config import Config


celery = Celery(__name__, broker=Config.CELERY_BROKER_URL, include=Config.CELERY_IMPORTS)


def init():
    from app.tasks import set_tasks

    set_tasks.delay()


def _get_tasks():
    tasks = celery.control.inspect().scheduled()
    return tasks[list(tasks.keys())[0]] if tasks is not None else []


def has_reserved_task(name, args):
    tasks = _get_tasks()
    tasks = list(filter(lambda t: t['request']['name'] == name and t['request']['args'] == args, tasks))
    return len(tasks) != 0
