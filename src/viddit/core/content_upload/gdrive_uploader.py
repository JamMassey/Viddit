import logging
import os

from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive

logger = logging.getLogger(__name__)


def upload_to_google_drive(video_file_path, creds_path, folder_id=None):
    """
    Uploads a video file to Google Drive using the PyDrive library.

    Args:
        video_file_path (str): The path to the MP4 video file to upload.
        folder_id (str, optional): The ID of the Google Drive folder to upload the video file to. Defaults to None.

    Returns:
        str: The ID of the uploaded file in Google Drive.
    """
    # Authenticate with Google Drive using PyDrive
    gauth = GoogleAuth()
    try:
        gauth.LoadCredentialsFile(creds_path)
    except FileNotFoundError:
        gauth.credentials = None
    # If the credentials are invalid or expired, refresh them
    if gauth.credentials is None or gauth.credentials.invalid:
        # Authenticate with Google Drive using the local webserver flow
        gauth = save_credentials_web_server_login()

    # Create a Google Drive client object
    drive = GoogleDrive(gauth)
    logger.info(f"Uploading {video_file_path} to Google Drive.")
    # Define the metadata for the video file
    file_metadata = {"title": os.path.basename(video_file_path)}
    if folder_id:
        file_metadata["parents"] = [{"kind": "drive#fileLink", "id": folder_id}]

    # Create a Google Drive file object for the video file
    file = drive.CreateFile()

    # Set the content of the Google Drive file object to the video file
    file.SetContentFile(video_file_path)

    # Upload the video file to Google Drive
    file.Upload()

    # Return the ID of the uploaded file in Google Drive
    return file["id"]


def get_credentials_web_server_login():
    """
    Authenticates with Google Drive using the web server login flow.

    Returns:
        GoogleAuth: The GoogleAuth object with the authenticated credentials.
    """
    logger.info("Authenticating with Google Drive using the web server login flow.")
    gauth = GoogleAuth()
    gauth.LocalWebserverAuth()
    return gauth


def save_credentials_web_server_login(creds_path):
    gauth = get_credentials_web_server_login()
    gauth.SaveCredentialsFile(creds_path)
    return gauth
