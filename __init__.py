from adapt.intent import IntentBuilder
from mycroft.skills.core import MycroftSkill, intent_handler
from mycroft import MycroftSkill, intent_file_handler
import json
from __future__ import print_function
import datetime
import pickle
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

SCOPES = ['https://www.googleapis.com/auth/calendar.events' + 'https://www.googleapis.com/auth/calendar.readonly']


class GetEvent(MycroftSkill):
    def __init__(self):
        MycroftSkill.__init__(self)

    @intent_handler(IntentBuilder("").require("event.by.name"))
    def handle_get_event_by_name(self):
        # Getting credentials for Google Calendar API
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

        # Query to get the event by name
        title = self.get_response('what\'s the name of the event')
        events_result = service.events().list(calendarId='primary',
                                              maxResults=1, singleEvents=True,
                                              orderBy='startTime', q=title).execute()
        events = events_result.get('items', [])

        if not events:
            self.speak('event not found')
        for event in events:
            start = event['start'].get('dateTime', event['start'].get('date'))
            location = event['location']
            description = event['description']
            self.speak_dialog('get.event', data={'start': start, 'title': title, 'location': location,
                                                 'description': description})

    @intent_handler(IntentBuilder("").require("attendees.by.event"))
    def handle_get_attendees_by_event(self):
        # Getting credentials for Google Calendar API
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

        # Query to get the event by name
        title = self.get_response('what\'s the name of the event')
        events_result = service.events().list(calendarId='primary',
                                              maxResults=1, singleEvents=True,
                                              orderBy='startTime', q=title).execute()
        events = events_result.get('items', [])

        attendemail = []
        attendname = []
        attendstatus = []
        i = 0

        if not events:
            print('event not found.')
        for event in events:
            start = event['start'].get('dateTime', event['start'].get('date'))

            eventid = event['id']

            attendees = event['attendees']
            l = len(attendees)
            while i != l:
                attendemail.append(attendees[i]['email'])
                attendstatus.append(attendees[i]['responseStatus'])
                attendname.append(attendees[i].get('displayName'))
                i = i + 1
        self.speak_dialog('attendees.list', data={'att': attendname})

    @intent_handler(IntentBuilder("").require("attendees.status").require('status'))
    def handle_get__attendees_status_by_event(self, message):
        # Getting credentials for Google Calendar API
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

        # Query to get the event by name
        title = self.get_response('what\'s the name of the event')
        events_result = service.events().list(calendarId='primary',
                                              maxResults=1, singleEvents=True,
                                              orderBy='startTime', q=title).execute()
        events = events_result.get('items', [])

        attendemail = []
        attendname = []
        attendstatus = []
        confattend = []
        notyetattend = []
        declattend = []
        tentattend = []
        i = 0
        j = 0
        k = 0
        if not events:
            print('event not found.')
        for event in events:
            start = event['start'].get('dateTime', event['start'].get('date'))

            eventid = event['id']

            attendees = event['attendees']
            l = len(attendees)
            while i != l:
                attendemail.append(attendees[i]['email'])
                attendstatus.append(attendees[i]['responseStatus'])
                attendname.append(attendees[i].get('displayName'))
                i = i + 1
            while k != l:
                if attendname[k] is None:
                    attendname[k] = attendemail[k]
                    k = k + 1
            while j != l:
                if attendees[j]['responseStatus'] == 'accepted':
                    confattend.append(attendees[j].get('displayName'))
                elif attendees[j]['responseStatus'] == 'needsAction':
                    notyetattend.append(attendees[j].get('displayName'))
                elif attendees[j]['responseStatus'] == 'declined':
                    declattend.append(attendees[j].get('displayName'))
                elif attendees[j]['responseStatus'] == 'tentative':
                    tentattend.append(attendees[j].get('displayName'))
                j = j + 1

        if message.data["status"] == "confirmed":
            self.speak_dialog('confirmed.attendees.list', data={'att': confattend})
        elif message.data["status"] == "did not take action":
            self.speak_dialog('notyet.attendees.list', data={'att': notyetattend})
        elif message.data["status"] == "decline":
            self.speak_dialog('declined.attendees.list', data={'att': declattend})
        elif message.data["status"] == "are tentative":
            self.speak_dialog('tentative.attendees.list', data={'att': tentattend})

    @intent_handler(IntentBuilder("").require("first.event"))
    def handle_get_first_event(self):
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

        # Call the Calendar API
        now = datetime.datetime.utcnow().isoformat() + 'Z'  # 'Z' indicates UTC time
        self.speak('Getting the first upcoming event')
        events_result = service.events().list(calendarId='primary', timeMin=now,
                                              maxResults=1, singleEvents=True,
                                              orderBy='startTime').execute()
        events = events_result.get('items', [])

        if not events:
            self.speak('No upcoming event found.')
        for event in events:
            start = event['start'].get('dateTime', event['start'].get('date'))
            title = event['summary']
            self.speak_dialog("ten.upcoming.events", data={"title": title, 'start': start})

    @intent_handler(IntentBuilder("").require("upcoming.events"))
    def handle_get_upcoming_ten_events(self):
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

        # Call the Calendar API
        now = datetime.datetime.utcnow().isoformat() + 'Z'  # 'Z' indicates UTC time
        self.speak('Getting the upcoming events')
        events_result = service.events().list(calendarId='primary', timeMin=now,
                                              maxResults=10, singleEvents=True,
                                              orderBy='startTime').execute()
        events = events_result.get('items', [])

        if not events:
            self.speak('No upcoming events found.')
        for event in events:
            start = event['start'].get('dateTime', event['start'].get('date'))
            # end = event['end'].get('dateTime', event['end'].get('date'))
            # description = event['description']
            title = event['summary']
            self.speak_dialog("ten.upcoming.events", data={"title": title, 'start': start})


def create_skill():
    return GetEvent()
