from fastapi import Query


def get_trimmed_query(name: str, *args, **kwargs):
    kwargs['alias'] = kwargs.get('alias', name)

    def query(q: str = Query(*args, **kwargs)) -> str:
        return q.strip()

    return query
