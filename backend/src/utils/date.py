import datetime


def today() -> datetime.date:
    """ e.g. 2020-08-12 """

    return datetime.date.today()


def n_days_ago(date: str) -> int:
    """ Args:
            date: format of today value

        Returns:
            day difference between date of today and the passed one """

    return (datetime.date.today() - string_2_date(date)).days


def string_2_date(date: str) -> datetime.date:
    """ Args:
            date: format of today value"""

    return datetime.datetime.strptime(date, '%Y-%m-%d').date()
