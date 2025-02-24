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