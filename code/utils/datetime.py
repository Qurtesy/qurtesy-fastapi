from datetime import date

def format_date(d: date):
    return f'{d.day:02}/{d.month:02}/{d.year}'