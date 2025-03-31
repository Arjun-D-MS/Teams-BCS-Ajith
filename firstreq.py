import sys
import requests
from datetime import datetime, timedelta
import pytz
from dateutil import parser
import json
import re

# Ensure login_token and choice are passed via command-line arguments hi
if len(sys.argv) < 3:
    print("Usage: python script.py <login_token> <choice> <TIME/JOBIDNUMBER>")
    sys.exit(1)

# The login token and choice passed as arguments
login_token = sys.argv[1]
choice = sys.argv[2]

# If choice is 1, sys.argv[3] should be TIME; if choice is 2 or 3, sys.argv[3] should be JOBIDNUMBER
if choice == '1' and len(sys.argv) < 4:
    print("Usage: python script.py <login_token> 1 <TIME>")
    sys.exit(1)

if choice in ['2', '3'] and len(sys.argv) < 4:
    print("Usage: python script.py <login_token> <choice> <JOBIDNUMBER>")
    sys.exit(1)

# Choice 1: Fetch jobs based on time period
if choice == '1':
    time_period = sys.argv[3]  # TIME is passed here

    time_deltas = {
        'fifteenMinutes': timedelta(minutes=15),
        'thirtyMinutes': timedelta(minutes=30),
        'oneHour': timedelta(hours=1),
        'twoHours': timedelta(hours=2),
        'fourHours': timedelta(hours=4),
        'eightHours': timedelta(hours=8),
        'twelveHours': timedelta(hours=12),
        'oneDay': timedelta(days=1)
    }

    if time_period not in time_deltas:
        raise ValueError("Invalid time period. Choose from 'fifteenMinutes', 'thirtyMinutes', 'oneHour', 'twoHours', 'fourHours', 'eightHours', 'twelveHours', 'oneDay'.")

    end_time = datetime.now(pytz.timezone('Asia/Kolkata'))
    start_time = end_time - time_deltas[time_period]

    start_time_str = start_time.strftime('%Y-%m-%d %H:%M:%S')
    end_time_str = end_time.strftime('%Y-%m-%d %H:%M:%S')

    url = "https://symphonyback.com:3011/symphony-dnd/api/jobs/nodequeue/job"

    params = {
        'globalSearch': '',
        'pageSize': 100,
        'pageNumber': 1,
        'jobStatus': 'Failed',
        'processEngine': '',
        'sapJobFilter': '',
        'startDate': start_time_str,
        'datePicker': 'today',
        'endDate': end_time_str,
        'order': 'desc',
        'orderBy': 'job_name',
        'activeTab': 'All Jobs',
        'processEngineFilter': ''
    }

    headers = {
        'Authorization': f'{login_token}'
    }

    response = requests.get(url, headers=headers, params=params)

    if response.status_code == 200:
        data = response.json()

        if data["flag"] == "success":
            job_data = data["data"][0]["totalData"]

            filtered_jobs = []
            for job in job_data:
                job_info = {}

                # Check and parse job ID, or set as 'N/A' if not found
                job_info["JobID"] = job.get("job_name", "N/A")
                
                # Check and parse job title, or set as 'N/A' if not found
                job_info["JobName"] = job.get("job_title", "N/A")
                
                # Check and parse node name, or set as 'N/A' if not found
                job_info["JobNode"] = job.get("nodeName", "N/A")

                # Try parsing start and end times, or set as 'N/A' if invalid or missing
                try:
                    job_start_time = parser.parse(job.get("startTime", "N/A")).astimezone(pytz.timezone('Asia/Kolkata')) if job.get("startTime") != "N/A" else "N/A"
                    job_end_time = parser.parse(job.get("endTime", "N/A")).astimezone(pytz.timezone('Asia/Kolkata')) if job.get("endTime") != "N/A" else "N/A"
                    
                    if job_start_time != "N/A":
                        job_info["StartTime"] = job_start_time.strftime('%Y-%m-%d %H:%M:%S')
                    else:
                        job_info["StartTime"] = "N/A"

                    if job_end_time != "N/A":
                        job_info["EndTime"] = job_end_time.strftime('%Y-%m-%d %H:%M:%S')
                    else:
                        job_info["EndTime"] = "N/A"
                except (ValueError, TypeError):
                    job_info["StartTime"] = "N/A"
                    job_info["EndTime"] = "N/A"

                filtered_jobs.append(job_info)

            if filtered_jobs:
                print(f"##gbStart##copilot_ctable_data1##splitKeyValue##{json.dumps(filtered_jobs)}##gbEnd##")
            else:
                print("No jobs failed in the given time configuration")
        else:
            print("No data found or error in the response.")
    else:
        print(f"Failed to fetch data. HTTP Status code: {response.status_code}")
        #App ID: 102792

# Choice 2: Fetch job details using jobIdNumber
elif choice == '2':
    job_id_number = int(sys.argv[3])  # JOBIDNUMBER is passed here

    end_date = datetime.now()
    start_date = end_date - timedelta(hours=24)

    start_date_str = start_date.strftime('%Y-%m-%d')
    end_date_str = end_date.strftime('%Y-%m-%d')

    job_url = "https://symphonyback.com:3011/symphony-dnd/api/jobs/nodequeue/job"

    params = {
        "globalSearch": str(job_id_number),
        "pageSize": 100,
        "pageNumber": 1,
        "jobStatus": "Failed",
        "processEngine": "",
        "sapJobFilter": "",
        "startDate": "",
        "datePicker": "today",
        "endDate": end_date_str,
        "order": "desc",
        "orderBy": "job_name",
        "activeTab": "All Jobs",
        "processEngineFilter": ""
    }

    headers = {
        "accept": "application/json, text/plain, */*",
        "accept-language": "en-US,en;q=0.9",
        "authorization": login_token,
        "if-none-match": 'W/"9c7-L8YYLvKZ1NOjhzYp+xBzngy5jKk"',
        "msalauthorization": "",
        "origin": "https://symphony4cloud.com",
        "priority": "u=1, i",
        "referer": "https://symphony4cloud.com/",
        "sec-ch-ua": '"Not(A:Brand";v="99", "Google Chrome";v="133", "Chromium";v="133"',
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": '"Windows"',
        "sec-fetch-dest": "empty",
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "cross-site",
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Safari/537.36",
        "x-appcorrelationid": "cdIfPICu-",
        "x-messageid": "fqtR2Jml-.1740718652217"
    }

    response = requests.get(job_url, headers=headers, params=params)

    if response.status_code == 200:
        data = response.json()

        found_node_id = None
        job_title = None
        node_name = None
        for job in data['data'][0]['totalData']:
            if job.get('job_name') == job_id_number:
                found_node_id = job.get('nodeId')
                job_title = job.get('job_title', 'N/A')
                node_name = job.get('nodeName', 'N/A')
                break

        if found_node_id:
            second_api_url = f"https://symphonyback.com:3011/symphony-dnd/api/jobs/{job_id_number}/node/{found_node_id}/logs"

            second_api_response = requests.get(second_api_url, headers=headers)

            if second_api_response.status_code == 200:
                second_api_data = second_api_response.json()
                if second_api_data.get("flag") == "success":
                    log_data = second_api_data['data']

                    # Check if the log data exceeds 100 lines
                    log_lines = log_data.split('\n')
                    if len(log_lines) > 100:
                        # Log is too large to view
                        result = [{
                            "Job_Name": job_title,
                            "job_Id": job_id_number,
                            "Node_Name": node_name,
                            "message": f"The log is too large to view Please open the Job {job_id_number} to view the logs."
                        }]
                    else:
                        # Remove all double quotes (") from the log data
                        sanitized_log_data = log_data.replace('"', '')  # Remove quotation marks

                        # Replace multiple spaces with a single space, and remove leading/trailing spaces
                        sanitized_log_data = re.sub(r'\s+', ' ', sanitized_log_data).strip()

                        # Prepare the output for all logs without disturbing the JSON
                        result = [{
                            "Job_Name": job_title,
                            "job_Id": job_id_number,
                            "Node_Name": node_name,
                            "log": sanitized_log_data  # Pass the sanitized log data
                        }]

                    # Return the result (either log or the "too large" message)
                    output = json.dumps(result, ensure_ascii=False)
                    print(f"##gbStart##copilot_ctable_data##splitKeyValue##{output}##gbEnd##")
                else:
                    print("Failed to retrieve logs from the second API.")
            else:
                print(f"Failed to fetch data from second API. Status code: {second_api_response.status_code}")
        else:
            print(f"No job found with jobIdNumber {job_id_number}")
    else:
        print(f"Failed to fetch data from first API. Status code: {response.status_code}")
        
# Choice 3: Restart job based on jobIdNumber
elif choice == '3':
    job_id_number = int(sys.argv[3])  # JOBIDNUMBER is passed here

    end_date = datetime.now()
    start_date = end_date - timedelta(hours=24)

    start_date_str = start_date.strftime('%Y-%m-%d')
    end_date_str = end_date.strftime('%Y-%m-%d')

    job_url = "https://symphonyback.com:3011/symphony-dnd/api/jobs/nodequeue/job"

    params = {
        "globalSearch": str(job_id_number),
        "pageSize": 100,
        "pageNumber": 1,
        "jobStatus": "Failed",
        "processEngine": "",
        "sapJobFilter": "",
        "startDate": "",
        "datePicker": "today",
        "endDate": end_date_str,
        "order": "desc",
        "orderBy": "job_name",
        "activeTab": "All Jobs",
        "processEngineFilter": ""
    }

    headers = {
        "accept": "application/json, text/plain, */*",
        "accept-language": "en-US,en;q=0.9",
        "authorization": login_token,
        "if-none-match": 'W/"9c7-L8YYLvKZ1NOjhzYp+xBzngy5jKk"',
        "msalauthorization": "",
        "origin": "https://symphony4cloud.com",
        "priority": "u=1, i",
        "referer": "https://symphony4cloud.com/",
        "sec-ch-ua": '"Not(A:Brand";v="99", "Google Chrome";v="133", "Chromium";v="133"',
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": '"Windows"',
        "sec-fetch-dest": "empty",
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "cross-site",
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Safari/537.36",
        "x-appcorrelationid": "cdIfPICu-",
        "x-messageid": "fqtR2Jml-.1740718652217"
    }

    response = requests.get(job_url, headers=headers, params=params)

    if response.status_code == 200:
        data = response.json()

        found_node_id = None
        job_title = None
        node_name = None
        for job in data['data'][0]['totalData']:
            if job.get('job_name') == job_id_number:
                found_node_id = job.get('nodeId')
                job_title = job.get('job_title', 'N/A')
                node_name = job.get('nodeName', 'N/A')
                break

        if found_node_id:
            restart_url = f'https://symphonyback.com:3011/symphony-dnd/api/jobs/{job_id_number}/node/{found_node_id}/restart'

            data = {
                "job_name": job_id_number,
                "nodeId": found_node_id,
                "nodeStatus": "Failed",
                "restartActionType": "restart_step"
            }

            restart_response = requests.post(restart_url, headers=headers, json=data)

            if restart_response.status_code == 200 and restart_response.json().get('flag') == 'success':
                output = json.dumps([{
                    "Job_Name": job_title,
                    "job_Id": job_id_number,
                    "Node_Name": node_name,
                    "Restart_Status": "restarted successfully"
                }], ensure_ascii=False)
            else:
                output = f"Failed to restart job {job_id_number}"
        else:
            output = f"No job found with jobIdNumber {job_id_number}"

    else:
        output = f"Failed to fetch data from the first API. Status code: {response.status_code}"

    print(f"##gbStart##copilot_ctable_data##splitKeyValue##{output}##gbEnd##")
