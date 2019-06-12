"""Main.

This script accesses google calendar through the calendar API to update or
create events.
"""
import datetime
import pickle
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

SCOPES = ['https://www.googleapis.com/auth/calendar.events']
CALENDAR_NAME = "Pearl GPU's"
EVENT_NAME = "satyaway pearl5 full"


def main():
    """Shows basic usage of the Google Calendar API.
    Prints the start and name of the next 10 events on the user's calendar.
    """
    creds = None
    # The file token.pickle stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server()
        # Save the credentials for the next run
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)

    service = build('calendar', 'v3', credentials=creds)

    # Get a list of calendars and chooses the correct one
    calendars = get_calendar_list(service)
    calendar_id = [calendar['id'] for calendar in calendars
                   if calendar['summary'] == CALENDAR_NAME][0]  # Assumes
    # calendars are uniquely named.

    # Get a list of events and chooses the correct one
    events = get_events_list(service, calendar_id)
    event_id = [event['id'] for event in events
                if event['summary'] == EVENT_NAME]  # Assumes events are
    # uniquely named.

    # Get end date since this is used in both cases.
    cdt = datetime.datetime.now()  # cdt = current date time
    end_date = cdt + datetime.timedelta(days=4)
    end_date = "{:04d}-{:02d}-{:02d}".format(end_date.year, end_date.month,
                                             end_date.day)
    if not event_id:
        print("Event not found. Creating a new event.")

        # Set up start time
        cdt = "{:04d}-{:02d}-{:02d}".format(cdt.year, cdt.month, cdt.day)

        # Create event
        event = {
            'summary': EVENT_NAME,
            'start': {
                'date': cdt
            },
            'end': {
                'date': end_date
            },
            'reminders': {
                'useDefault': False
            }
        }
        event = service.events().insert(calendarId=calendar_id, body=event)\
            .execute()
        print("Event created: {}".format(event.get('htmlLink')))

    else:
        event = service.events().get(calendarId=calendar_id,
                                     eventId=event_id[0]).execute()

        # updates event to end 3 days after whenever this script was run
        event['end'] = {'date': end_date}
        updated_event = service.events().update(calendarId=CALENDAR_NAME,
                                                eventId=event_id[0],
                                                body=event).execute()
        print("Updated: {}".format(updated_event['updated']))


def get_events_list(service, calendar_id, max_results=50) -> list:
    """Get the next x events from a given calendar."""
    now = datetime.datetime.utcnow().isoformat() + 'Z'  # 'Z' indicates UTC.
    output_list = []

    events_result = service.events().list(calendarId=calendar_id, timeMin=now,
                                          maxResults=max_results,
                                          singleEvents=True,
                                          orderBy='startTime').execute()
    for event in events_result['items']:
        output_list.append(event)

    return output_list


def get_calendar_list(service) -> list:
    """Gets a list of calendars in the account."""
    page_token = None
    output_list = []

    while True:
        calendar_list = service.calendarList() \
            .list(pageToken=page_token).execute()
        for calendar_list_entry in calendar_list['items']:
            output_list.append(calendar_list_entry)
        page_token = calendar_list.get('nextPageToken')

        if not page_token:
            break

    return output_list


if __name__ == '__main__':
    main()
