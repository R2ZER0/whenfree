import os

SECRET_KEY = os.environ.get("SECRET_KEY", "secret-key-goes-here")
BASIC_AUTH_USERNAME = os.environ.get("BASIC_AUTH_USERNAME")
BASIC_AUTH_PASSWORD = os.environ.get("BASIC_AUTH_PASSWORD")

CALENDAR_SOURCE = os.environ.get("CALENDAR_SOURCE", "caldav")  # caldav or google

USERNAME = os.environ.get("WHENFREE_USERNAME", "")
CALDAV_URL = os.environ.get("CALDAV_URL")
CALDAV_USERNAME = os.environ.get("CALDAV_USERNAME")
CALDAV_PASSWORD = os.environ.get("CALDAV_PASSWORD")
CALENDARS_TO_INCLUDE = os.environ.get("CALENDARS_TO_INCLUDE", "").split(",")

GOOGLE_CREDENTIALS_DIR = os.environ.get("GOOGLE_CREDENTIALS_DIR")

CALENDAR_SETTINGS = {
    "earliestTime": "00:00",
    "latestTime": "24:00",
    "weekdays": [1, 2, 3, 4, 5, 6, 0],
    "firstDayOfWeek": 1,
    "ignoreAllDayEvents": True,
    "ignoreSameTimeEvents": True,
    "daysBefore": 14,
    "daysAfter": 14,
    "urlReplacement": "--DATE--",
}

TIMEZONE = os.environ.get("TIMEZONE", "Europe/London")
