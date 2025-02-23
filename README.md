# Website Monitoring and Recovery System

A automated system I built to monitor website health and perform recovery actions using Python, Docker, and Linux.

## Overview

I created a comprehensive website monitoring system that automatically detects downtime and performs recovery actions. The system runs on a cloud infrastructure and sends email notifications when issues are detected.

![diagram](https://github.com/Princeton45/website-monitoring-python/blob/main/images/diagram.png)


## How It Works

# Infrastructure Layer

- The system runs on a Linode Linux server
- All monitoring components are containerized using Docker for isolation and easy deployment

# Monitoring Process

- A Python script continuously runs inside the Docker container
- It performs regular HTTP checks on the target website
- The script also monitors the overall application status

# Issue Detection

- When the monitoring script detects a problem (HTTP errors or timeout)
- Two parallel processes are triggered:
  - Email notification system
  - Auto-recovery procedure

# Recovery Workflow

- The auto-recovery script attempts to restart the application
- If application restart fails, it can escalate to a server restart
- The system continuously monitors the recovery process

# Notification System

- Immediate email alerts are sent when issues are detected
- Additional notifications are sent if recovery attempts fail
- Success notifications are sent once the system is back online

# Continuous Monitoring

- After successful recovery, the system returns to its regular monitoring state
- The cycle continues to ensure constant website availability

## Technologies Used

- Python
- Linode Cloud Platform
- Docker
- Linux

## Implementation

1. **Cloud Server Setup**
   - Deployed a Linux server on Linode cloud platform
   
   ![Cloud Server Dashboard](suggest: Add a screenshot of your Linode dashboard showing the server)

2. **Docker Configuration**
   - Installed Docker on the remote server
   - Created and deployed a Docker container for the monitoring application

3. **Monitoring Script**
   - Developed a Python script that continuously checks website availability
   - Implemented HTTP response validation
   
   ![Monitoring Dashboard](suggest: Add a screenshot of your monitoring script output or logs)

4. **Notification System**
   - Created an email notification system using Python
   - Configured automated alerts for website downtime

5. **Auto-Recovery System**
   - Implemented automatic application and server restart functionality
   - Built failsafe mechanisms to prevent cascading failures

## Architecture

![System Architecture](suggest: Add a diagram showing the flow: Monitor -> Alert -> Recovery)

## Results

The system successfully:
- Monitors website health 24/7
- Sends immediate notifications during downtime
- Automatically recovers from common failure scenarios
- Runs in an isolated Docker container

## Contact

For any questions about this project, feel free to reach out:
[Your Contact Information]