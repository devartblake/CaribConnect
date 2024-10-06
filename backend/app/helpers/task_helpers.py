import logging

import requests

from app.core.db import get_database_session
from app.models import Record, User

logger = logging.getLogger(__name__)

def get_users_to_notify():
    """
    Fetches a list of users who need to be notified.
    You can modify the criteria based on your application needs.
    """
    try:
        with get_database_session() as session:  # Use context manager for the session
            users = session.query(User).filter(User.notify is True).all()  # Adjust your filter as needed
            logger.info(f"Fetched {len(users)} users to notify.")
            return users
    except Exception as e:
        logger.error(f"Error fetching users to notify: {e}")
        return []  # Return an empty list in case of an error


def cleanup_old_records_db(cutoff_date):
    """
    Deletes records older than the cutoff date from the database.
    Returns the number of records deleted.
    """
    try:
        with get_database_session() as session:
            old_records = session.query(Record).filter(Record.created_at < cutoff_date).delete()
            session.commit()  # Commit the transaction
            logger.info(f"Deleted {old_records} records older than {cutoff_date}.")
            return old_records
    except Exception as e:
        logger.error(f"Error cleaning up old records: {e}")
        return 0  # Return 0 in case of an error


def generate_report_db():
    """
    Generates a daily report.
    Returns the report content as a string.
    """
    try:
        with get_database_session() as session:
            report_data = session.query(Record).all()  # Replace with your query for report data

            # Example report content generation
            report_content = "Daily Report\n\n"
            for record in report_data:
                report_content += f"{record.id}: {record.details}\n"  # Adjust as necessary

            logger.info("Report generated successfully.")
            return report_content
    except Exception as e:
        logger.error(f"Error generating report: {e}")
        return "Error generating report"  # Return a default message in case of an error


def check_system_health():
    """
    Performs a basic health check on the system.
    Checks database connectivity and any other required checks.
    Returns True if healthy, False otherwise.
    """
    try:
        # Check database connectivity
        with get_database_session() as session:
            session.execute("SELECT 1")  # Simple query to check connectivity
        logger.info("Database is reachable.")
        return True
    except Exception as e:
        logger.error(f"Database is not reachable: {e}")
        return False

def fetch_api_data(api_url):
    """
    Helper function to poll an external API and return the response data.
    Args:
        api_url (str): The URL of the external API to poll.

    Returns:
        dict | None: Parsed JSON data if the request is successful, otherwise None.
    """
    try:
        response = requests.get(api_url)
        if response.status_code == 200:
            logger.info(f"Successfully fetched data from {api_url}.")
            return response.json()
        else:
            logger.error(f"Failed to fetch data from {api_url}. Status Code: {response.status_code}")
            return None
    except requests.exceptions.RequestException as e:
        logger.error(f"Error fetching data from {api_url}: {e}")
        return None

def process_data(data):
    """
    Process the data obtained from the external API.
    This function should be implemented based on your specific requirements.
    """
    # Implement your data processing logic here
    logger.info("Processing data from external API.")
    # Example: Save data to the database, update records, etc.
    with get_database_session() as session:
        # Assume you have a model named ExternalData
        # external_data = ExternalData(**data)
        # session.add(external_data)
        # session.commit()
        pass  # Replace with your processing logic

def create_backup():
    """
    Logic to create a database backup.
    This should be implemented based on your specific database requirements.
    """
    # Here you can use your database management tools or libraries to create a backup
    logger.info("Starting database backup...")
    # Example: Call your database backup command or script
    pass  # Replace with your actual backup logic

def clear_cache():
    """
    Clear existing cached data.
    Implement the logic to clear your cache here.
    """
    logger.info("Clearing cache...")
    # Implement your cache clearing logic here
    pass  # Replace with your actual cache clearing logic

def update_cache():
    """
    Update cache with fresh data.
    Implement the logic to fetch and update cache here.
    """
    logger.info("Updating cache with fresh data...")
    # Implement your cache updating logic here
    pass  # Replace with your actual cache updating logic
