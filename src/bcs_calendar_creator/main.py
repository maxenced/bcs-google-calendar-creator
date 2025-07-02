import logging
import yaml
import os.path
import click

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from bcs_calendar_creator.calendar import Category

# If modifying these scopes, delete the file token.json.
SCOPES = ["https://www.googleapis.com/auth/calendar"]


@click.command()
@click.option(
    "--no-override",
    is_flag=True,
    default=False,
    help="Prevent overriding existing data",
)
@click.option("--debug", is_flag=True, default=False, help="Enable debug mode")
def main(no_override, debug):
    loglevel = logging.INFO
    if debug:
        loglevel = logging.DEBUG
    logging.basicConfig(
        format="[%(name)s]: [%(asctime)s] [%(levelname)s] {%(filename)s:%(lineno)d} %(funcName)s # %(message)s",
        level=loglevel,
    )
    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file("token.json", SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file("credentials.json", SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open("token.json", "w") as token:
            token.write(creds.to_json())

    try:
        logging.info("Starting")
        service = build("calendar", "v3", credentials=creds)
        with open("src/bcs_calendar_creator/configuration.yaml", "r") as f:
            config = yaml.load(f, yaml.SafeLoader)
            for category, data in config.get("categories").items():
                logging.info(f"Working on {category}")
                c = Category(category, service, data)
                c.update()

    except HttpError as error:
        print(f"An error occurred: {error}")


if __name__ == "__main__":
    main()  # Click will parse command line arguments automatically
