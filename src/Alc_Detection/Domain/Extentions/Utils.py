def between(
    date, 
    start, 
    end, 
    inclusive_start=True, 
    inclusive_end=True
):
    if start > end:
        start, end = end, start
    lower_check = (date >= start) if inclusive_start else (date > start)
    upper_check = (date <= end) if inclusive_end else (date < end)
    return lower_check and upper_check