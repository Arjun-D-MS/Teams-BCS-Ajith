import sys
import requests
import json
from datetime import datetime, timedelta
import pytz
from dateutil import parser  # Import dateutil.parserhttps://github.com/Arjun-D-MS/test-BCS.git

def fetch_events(login_token, email, start_datetime_str, end_datetime_str, choice, user_timezone_str=None):
    # Microsoft Graph API endpoint for fetching calendar view events App ID: 102908 deleted, new App ID: 102924
    url = f"https://graph.microsoft.com/v1.0/users/{email}/calendarView"
    
    # Prepare the headers for the request
    headers = {
        'Authorization': f'Bearer {login_token}',
        'Content-Type': 'application/json'
    }
    
    # Set up parameters to filter events by start and end date
    params = {
        'startDateTime': start_datetime_str,
        'endDateTime': end_datetime_str,
        '$select': 'subject,id,start,end,organizer,attendees'
    }
    
    # Send the request to the API
    response = requests.get(url, headers=headers, params=params)
    
    # Check if the request was successful
    if response.status_code == 200:
        data = response.json()
        events = data.get('value', [])
        
        if not events:
            # If no events are found, return the message
            mention_date = start_datetime_str.split('T')[0]  # Get the date part from the start_datetime
            no_meetings_message = {
                "Meetings": f"No meetings available in the specified date ({mention_date})"
            }
            print(f"##gbStart##copilot_ctable_data##splitKeyValue##[{json.dumps(no_meetings_message)}]##gbEnd##")
            return  # Exit the function early since there are no meetings
        
        output = []  # To hold the final result
        output1 = []

        # Check if user timezone is provided, if not default to UTC
        if user_timezone_str:
            user_timezone = pytz.timezone(user_timezone_str)
        else:
            user_timezone = pytz.utc  # Default to UTC if no timezone is passed

        for event in events:
            subject = event.get('subject', "")
            
            # Skip event if subject contains the word "canceled" (case insensitive)
            if "canceled" in subject.lower():
                continue

            event_id = event.get('id')
            
            # Get the start and end datetime in UTC
            start_time = event.get('start', {}).get('dateTime')
            end_time = event.get('end', {}).get('dateTime')
            
            # Convert the UTC time to user timezone or UTC (if no timezone provided)
            start_time_formatted = convert_datetime_format(start_time, user_timezone)
            end_time_formatted = convert_datetime_format(end_time, user_timezone)
            
            # Calculate the reminder time (5 minutes before the start time)
            reminder_time = get_reminder_time(start_time, user_timezone)
            
            # Get the organizer's email address
            organizer_email = event.get('organizer', {}).get('emailAddress', {}).get('address')
            
            # Collect all attendees' emails
            attendees = event.get('attendees', [])
            attendees_emails = [attendee['emailAddress']['address'] for attendee in attendees]
            start_time = event.get('start', {}).get('dateTime')
            end_time = event.get('end', {}).get('dateTime')
            combined_time = format_combined_datetime(start_time, end_time, user_timezone)
            
            # Format the result
            result1 = {
                'Requested_Meetings_subject': subject,
                #'Meeting_starting_time': start_time_formatted,
                #'Meeting_ending_time': end_time_formatted,
                'Meeting_Time': combined_time, 
                'organizer_email': organizer_email
                #'attendees_emails': ";".join(attendees_emails)  # Join emails with semicolons
            }
            
            output.append(result1)

            result2 = {
                'Requested_Meetings_subject': subject,
                #'Meeting_starting_time': start_time_formatted,
                #'Meeting_ending_time': end_time_formatted,
                #'organizer_email': organizer_email,
                'attendees_emails': ";".join(attendees_emails)  # Join emails with semicolons
            }
            output1.append(result2)
        # Print the output in the required format
        if choice == '1':
           print(f"##gbStart##copilot_ctable1_data##splitKeyValue##{json.dumps(output)}##gbEnd##")
        elif choice == '2':   
           print(f"##gbStart##copilot_ctable2_data##splitKeyValue##{json.dumps(output1)}##gbEnd##")
        elif  choice == '3':
            print(f"##gbStart##copilot_ctable1_data##splitKeyValue##{json.dumps(output)}##gbEnd##")
            print(f"##gbStart##copilot_ctable2_data##splitKeyValue##{json.dumps(output1)}##gbEnd##")
        else:
            no_choice_message = {
                "Meetings": f"Wrong Choice"
            }
            print(f"##gbStart##copilot_ctable_data##splitKeyValue##[{json.dumps(no_choice_message)}]##gbEnd##")

    else:
        print(f"Failed to fetch events. Status code: {response.status_code}")
        try:
            # Try to print the error response if it's JSON
            print(f"Error response: {response.json()}")
        except json.JSONDecodeError:
            # If not JSON, print the raw text
            print(f"Error response (not JSON): {response.text}")

def convert_datetime_format(datetime_str, user_timezone):
    """Converts a datetime string from ISO format (UTC) to 'YYYY-MM-DD HH:MM:SS' format in user's timezone."""
    try:
        # Parse the ISO format datetime string (assume it's UTC time)
        dt_utc = parser.parse(datetime_str)  # Use dateutil.parser.parse() to handle ISO format
        dt_utc = pytz.utc.localize(dt_utc)  # Localize the datetime to UTC
        
        # Convert to user's timezone (if provided) or default to UTC
        dt_user_tz = dt_utc.astimezone(user_timezone)
        
        # Convert to the desired format 'YYYY-MM-DD HH:MM:SS'
        return dt_user_tz.strftime('%Y-%m-%d %H:%M:%S')
    except Exception as e:
        print(f"Error converting datetime: {e}")
        return None

def get_reminder_time(start_time_str, user_timezone):
    """Calculates the reminder time (5 minutes before the event's start time)."""
    try:
        # Parse the start time
        start_time = parser.parse(start_time_str)
        start_time = pytz.utc.localize(start_time)  # Localize to UTC

        # Convert the start time to the user's timezone
        start_time_user_tz = start_time.astimezone(user_timezone)
        
        # Subtract 5 minutes to get the reminder time
        reminder_time = start_time_user_tz - timedelta(minutes=5)
        
        # Format the reminder time to 'YYYY-MM-DD HH:MM:SS'
        return reminder_time.strftime('%Y-%m-%d %H:%M:%S')
    except Exception as e:
        print(f"Error calculating reminder time: {e}")
        return None

def format_combined_datetime(start_time_str, end_time_str, user_timezone):
    """Formats start and end times into 'Month day suffix stime-etime' format."""
    try:
        start_dt = parser.parse(start_time_str)
        end_dt = parser.parse(end_time_str)
        start_dt = pytz.utc.localize(start_dt).astimezone(user_timezone)
        end_dt = pytz.utc.localize(end_dt).astimezone(user_timezone)

        def day_suffix(day):
            return (
                f"{day}st" if 10 < day % 100 < 20 else
                {1: "st", 2: "nd", 3: "rd"}.get(day % 10, "th")
            )

        formatted_start = start_dt.strftime(f"%B {day_suffix(start_dt.day)} %H:%M")
        formatted_end = end_dt.strftime("%H:%M")

        return f"{formatted_start}-{formatted_end}"
    except Exception as e:
        print(f"Error formatting datetime: {e}")
        return None


if __name__ == "__main__":
    # Get command line arguments
    login_token = sys.argv[1]      # Login token for authentication
    start_datetime_str = sys.argv[2]  # Start datetime in ISO format
    end_datetime_str = sys.argv[3]    # End datetime in ISO format
    email = sys.argv[4]       
    choice = sys.argv[5]    # Email passed as sys.argv[4]
    
    # Check if timezone argument is passed; if not, set to None
    user_timezone_str = sys.argv[6] if len(sys.argv) > 6 else None
    
    # Call the function to fetch events
    fetch_events(login_token, email, start_datetime_str, end_datetime_str, choice, user_timezone_str)
