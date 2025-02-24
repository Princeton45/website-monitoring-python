# Website Monitoring and Recovery System

A automated system I built to monitor website health and perform recovery actions using Python, Docker, and Linux.

## Overview

I created a comprehensive website monitoring system that automatically detects downtime and performs recovery actions. The system runs on a cloud infrastructure and sends email notifications when issues are detected.

![diagram](https://github.com/Princeton45/website-monitoring-python/blob/main/images/diagram.png)


## How It Works

## Infrastructure Layer

- The application is hosted on a Linode Linux server.
- The application runs inside a Docker container on the server.
- Remote server management is performed using the Linode API for rebooting and SSH for container management.

## Monitoring Process

- **Regular Checks:**  
  The script uses the `schedule` library to perform HTTP GET requests every 5 minutes against the application’s endpoint (`http://45.79.203.107:8080/`).
  
- **Health Determination:**  
  A response with a status code of 200 indicates that the application is running normally. Any other status code or an inability to reach the application triggers the recovery process.

## Issue Detection and Notification

- **Detection:**  
  - If the HTTP response status is not 200, the application is assumed to have an issue.
  - If an exception occurs during the HTTP request (for example, if the application is completely unreachable), the error is caught and processed.
  
- **Notification:**  
  An email notification is sent via Gmail’s SMTP server with details of the issue, immediately alerting you.

## Recovery Workflow

1. **Container Restart:**  
   - If an HTTP request returns a non-200 status, the script attempts to restart the Docker container by connecting via SSH.
   
2. **Server Reboot and Container Restart:**  
   - If a connection error occurs (suggesting that the application might be completely inaccessible), the script escalates the recovery by rebooting the Linode server.
   - The reboot is initiated using the Linode API. Once the server is back online, the Docker container is restarted using an SSH command.

## Continuous Operation

- The script runs in an infinite loop:
  - The monitoring task is triggered every 5 minutes.
  - After any recovery actions, the script returns to its normal monitoring state.
- Environment variables are used to securely provide:
  - `EMAIL_ADDRESS` and `EMAIL_PASSWORD` for SMTP authentication.
  - `LINODE_TOKEN` for access to the Linode API.
- SSH key-based authentication is used for accessing the remote server, so ensure that the key file path is correctly configured.

## Technologies Used

- Python
- Linode Cloud Platform
- Docker
- Linux

## Implementation

1. **Cloud Server Setup**
   - Deployed a Linux server on Linode cloud platform
   
   ![linode](https://github.com/Princeton45/website-monitoring-python/blob/main/images/linode.png)

2. **Docker Configuration**
   - Installed Docker on the remote server

   https://docs.docker.com/engine/install/ubuntu/

   - Created and deployed an Nginx Docker container for the web application we're monitoring
   
   `docker run -d -p 8080:80 nginx`

    ![docker-run](https://github.com/Princeton45/website-monitoring-python/blob/main/images/docker-run.png)

    ![8080](https://github.com/Princeton45/website-monitoring-python/blob/main/images/8080.png)


3. **Monitoring Script & Notification System**
   - Developed a Python script that continuously checks website availability every 5 minutes
   - Implemented HTTP response validation
   - Created an email notification system using Python
   - Configured automated alerts for website downtime

Below is a test of the python script sending a notification to me because it detected
the app was down (instead of response status of `200`, it can still tell me whatever 
response code it is getting other than `200`. I just tested the `else:` statement in the `monitor_application` function).

   ![app-down](https://github.com/Princeton45/website-monitoring-python/blob/main/images/app-down.png)

Below is a test of the script sendming a notification because it can't reach the Nginx webserver at all, no response code other than the message "Failed to establish a new connection"

   ![server-down](https://github.com/Princeton45/website-monitoring-python/blob/main/images/server-down.png)


5. **Auto-Recovery System**
   - Implemented automatic application and server restart functionality
   - Basically, if the application is in the docker container, but we're getting an HTTP response
   other than 200, it will restart the application.
   - If the application is not accessible at all and it can't establish a connection to the IP,
   we will assume it's a server issue so the server then the docker application will be restarted.

```python
import requests               # To make HTTP requests
import smtplib                # To send emails using SMTP
import os                     # To get environment variables
import paramiko               # To establish SSH connections and execute remote commands
import linode_api4            # To interact with Linode API for server management
import time                   # To add sleep delays between operations
import schedule               # To schedule periodic execution of functions

# Retrieve environment variables for email and Linode access
EMAIL_ADDRESS = os.environ.get('EMAIL_ADDRESS')
EMAIL_PASSWORD = os.environ.get('EMAIL_PASSWORD')
LINODE_TOKEN = os.environ.get('LINODE_TOKEN')

def restart_server_and_container():
    """
    Reboots the Linode server and restarts the application container.
    This function reboots the server, waits until the server is running again,
    and then calls the restart_container function to restart the application.
    """
    print('Rebooting the server...')
    
    client = linode_api4.LinodeClient(LINODE_TOKEN)
    
    nginx_server = client.load(linode_api4.Instance, 72511363)
    
    nginx_server.reboot()
    
    while True:
        nginx_server = client.load(linode_api4.Instance, 72511363)
        
        if nginx_server.status == 'running':
            time.sleep(5)
            restart_container()
            break 

def send_notification(email_msg):
    """
    Sends an email notification using SMTP.
    
    Args:
        email_msg (str): The message to be sent in the email body.
    """
    print('Sending an email...')
    
    # Connect to Gmail's SMTP server on the necessary port
    with smtplib.SMTP('smtp.gmail.com', 587) as smtp:
        smtp.starttls()           
        smtp.ehlo()               
        smtp.login(EMAIL_ADDRESS, EMAIL_PASSWORD)  
        
        msg = f"Subject: SITE DOWN\n{email_msg}"
        
        smtp.sendmail(EMAIL_ADDRESS, EMAIL_ADDRESS, msg)

def restart_container():
    """
    Restarts the application container running on a remote server using SSH.
    """
    print('Restarting the application...')
    
    ssh = paramiko.SSHClient()
    
    # Automatically add the server's SSH key to known hosts (for simplicity)
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    ssh.connect(
        hostname='45.79.203.107', 
        username='root', 
        key_filename='C:/Users/14435/.ssh/id_ed25519'
    )
    
    # Execute a command to restart the docker container by its container ID
    stdin, stdout, stderr = ssh.exec_command('docker start 18d59cfb7e1d')
    
    # Print the output lines from the execution for debugging purposes
    print(stdout.readlines())
    
    ssh.close()
    
    print('Application Restarted')
    
def monitor_application():
    """
    Monitors the application by sending an HTTP GET request to its endpoint.
    If the application is down or not accessible, sends an email notification and restarts the container or the server.
    """
    try:
        # Attempt to GET the application's homepage (or health endpoint)
        response = requests.get('http://45.79.203.107:8080/')
        
        # Check if the application returned an OK status code (200)
        if response.status_code == 200:
            print('Application is running successfully!')
        else:
            # If the application response code is not 200, handle it as an error state
            print('Application Down. Fix it.')
            message = f"Application returned {response.status_code}"
            
            send_notification(message)
            
            # Attempt to restart the container to bring the application back up
            restart_container()
                
    except Exception as ex:
        # In case of any connection error, log the error and send a notification
        print(f'Connection error happened: {ex}')
        message = "Application not accessible at all."
        
        # Send an email that the application is completely inaccessible
        send_notification(message)
        
        restart_server_and_container()
        
# Schedule monitor_application to run every 5 minutes
schedule.every(5).minutes.do(monitor_application)

# Continuously check for scheduled tasks and run them
while True:
    schedule.run_pending()
```