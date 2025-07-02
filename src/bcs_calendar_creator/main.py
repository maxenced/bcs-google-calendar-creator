import logging
import yaml
import os.path
import sys
import click
import yamale

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from bcs_calendar_creator.calendar import Category
from bcs_calendar_creator.logging_config import setup_logging

# If modifying these scopes, delete the file token.json.
SCOPES = ["https://www.googleapis.com/auth/calendar"]


@click.command()
@click.option(
    "--no-override",
    is_flag=True,
    default=False,
    help="Prevent overriding existing data. If set, overlaping event won't be deleted",
)
@click.option("--debug", is_flag=True, default=False, help="Enable debug mode")
@click.option(
    "--target",
    type=str,
    help="Filter to only one category. Add category key as value. Ex: --target ateliers_level3",
)
@click.option(
    "--prune",
    type=str,
    help="Prune all future events in one category. Add category key as value. Ex: --prune ateliers_level3",
)
def main(no_override: bool, debug: bool, target: str, prune: str):
    # Set up logging with colored output
    setup_logging(debug=debug)

    # Validate configuration file against schema
    config_path = "src/bcs_calendar_creator/configuration.yaml"
    schema_path = "src/bcs_calendar_creator/configuration.yaml.schema"

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
        with open(config_path, "r") as f:
            config = yaml.load(f, yaml.SafeLoader)
            try:
                logging.info("Validating configuration file against schema")
                schema = yamale.make_schema(schema_path)
                data = yamale.make_data(content=yaml.dump(config))
                yamale.validate(schema, data, strict=False)
                logging.info("Configuration validation successful")
            except yamale.YamaleError as e:
                logging.error(f"Configuration validation failed: {e}")
                sys.exit(1)
            if prune:
                logging.info(f"Pruning {target}")

            elif target:
                logging.info(f"Filter on {target}")
                data = config.get("categories").get(target, {})
                if not data:
                    logging.warning(f"Category {target} not found")
                    sys.exit(1)
                else:
                    c = Category(target, service, data)
                    c.update()
            else:
                for category, data in config.get("categories").items():
                    logging.info(f"Working on {category}")
                    c = Category(category, service, data)
                    c.update(no_override)

    except HttpError as error:
        print(f"An error occurred: {error}")


if __name__ == "__main__":
    main()  # Click will parse command line arguments automatically
