from typing import List, Union, Tuple

import datetime
import os.path
import pytz

from pathlib import Path
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from whenfree.settings import GOOGLE_CREDENTIALS_DIR

# If modifying these scopes, delete the file token.json.
SCOPES = ["https://www.googleapis.com/auth/calendar.readonly"]


def _parse_google_date(obj) -> datetime.datetime:
    if "dateTime" in obj:
        dt = datetime.datetime.fromisoformat(obj["dateTime"].replace("Z", "+00:00"))
        return dt.replace(tzinfo=pytz.utc)

    elif "date" in obj:
        return (
            datetime.datetime.strptime(obj["date"], "%Y-%m-%d")
            .replace(tzinfo=pytz.utc)
            .date()
        )

    else:
        raise NotImplementedError


def parse_google_start_end(
    start: Union[datetime.datetime, datetime.date],
    end: Union[datetime.datetime, datetime.date],
) -> Tuple[datetime.datetime, datetime.datetime, bool]:
    """
    Returns tuple of (start datetime, end datetime, is_all_day bool)
    """
    start_dt = _parse_google_date(start)
    end_dt = _parse_google_date(end)
    is_all_day = False

    # Check for all-day events
    if isinstance(start_dt, datetime.datetime) and isinstance(
        end_dt, datetime.datetime
    ):
        if start_dt.time() == datetime.time.min and end_dt.time() == datetime.time.min:
            is_all_day = True

    elif isinstance(start_dt, datetime.date):
        is_all_day = True

    return (start_dt, end_dt, is_all_day)


def get_google_events_raw(
    start: Union[datetime.datetime, datetime.date],
    end: Union[datetime.datetime, datetime.date],
    calendar_ids: List[str],
):
    creds_dir = Path(GOOGLE_CREDENTIALS_DIR or ".")
    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file(
            (creds_dir / "token.json").as_posix(), SCOPES
        )
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                (creds_dir / "credentials.json").as_posix(), SCOPES
            )
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open(creds_dir / "token.json", "w") as token:
            token.write(creds.to_json())

    try:
        service = build("calendar", "v3", credentials=creds)

        # Call the Calendar API
        if isinstance(start, datetime.date):
            start = datetime.datetime.combine(start, datetime.datetime.min.time())

        if isinstance(end, datetime.date):
            end = datetime.datetime.combine(end, datetime.datetime.min.time())

        start_str = start.isoformat() + "Z"  # 'Z' indicates UTC time
        end_str = end.isoformat() + "Z"

        events = list()

        for cal_id in calendar_ids:
            events_result = (
                service.events()
                .list(
                    calendarId=cal_id,
                    timeMin=start_str,
                    timeMax=end_str,
                    maxResults=250,
                    singleEvents=True,
                    orderBy="startTime",
                )
                .execute()
            )
            events.extend(events_result.get("items", []))

        if not events:
            print("No events found.")
            return list()

        return events

    except HttpError as error:
        print(f"An error occurred: {error}")
