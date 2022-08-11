from datetime import datetime as dt


def year(request):
    year = dt.now().year
    return {
        'year': year,
    }
