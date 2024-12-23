from datetime import datetime


def format_date(date_str: str) -> str:
    """Convert date string to YYYY-MM-DD format"""
    date_obj = datetime.strptime(date_str, "%Y-%m-%d")
    return date_obj.strftime("%Y-%m-%d")
