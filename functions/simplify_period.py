from itertools import groupby
from operator import itemgetter

def format_periods(dates):
    """
    Regroupe les périodes consécutives de type 'mois-year'
    sous forme de ranges (ex: Jan 2022 - Dec 2022).
    """
    if len(dates) == 0:
        return ""

    dates = sorted(dates)
    yms = [d.year * 12 + d.month for d in dates]

    grouped = []
    start_index = 0

    for i in range(1, len(dates)):
        if yms[i] != yms[i - 1] + 1:
            grouped.append((dates[start_index], dates[i - 1]))
            start_index = i

    grouped.append((dates[start_index], dates[-1]))

    formatted_periods = []
    for start_date, end_date in grouped:
        if start_date == end_date:
            formatted_periods.append(start_date.strftime("%B %Y"))
        else:
            formatted_periods.append(f"{start_date.strftime('%B %Y')} - {end_date.strftime('%B %Y')}")

    return ", ".join(formatted_periods)
