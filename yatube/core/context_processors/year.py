import datetime as dt


def year(request):
    """Добавляет переменную с текущим годом."""
    time = dt.datetime.now()
    return {
        'year': int(time.strftime("%Y"))
    }
