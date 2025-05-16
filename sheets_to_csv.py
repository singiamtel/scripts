#!/usr/bin/env -S uv run --script
# /// script
# dependencies = [
#   "google-api-python-client",
#   "google-auth",
# ]
# ///

import json
import argparse
import io
import sys
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload
from google.oauth2 import service_account
from googleapiclient.errors import HttpError


def get_gdrive_service(key_file):
    """Gets an authorized Google Drive API service instance using a service account."""
    # Define the required scopes
    SCOPES = ["https://www.googleapis.com/auth/drive.readonly"]

    # Authenticate using the service account key file
    credentials = service_account.Credentials.from_service_account_file(
        key_file, scopes=SCOPES
    )

    # Build the Drive API service
    service = build("drive", "v3", credentials=credentials)
    return service, credentials


def get_service_account_email(key_file):
    """Extract the service account email from the key file."""
    with open(key_file, "r") as f:
        key_data = json.load(f)
    return key_data.get("client_email")


def download_sheet_as_csv(service, spreadsheet_id, output_path, service_account_email):
    """Downloads a Google Sheet as CSV."""
    try:
        # Export the Google Sheet as CSV
        request = service.files().export_media(
            fileId=spreadsheet_id, mimeType="text/csv"
        )

        fh = io.BytesIO()
        downloader = MediaIoBaseDownload(fh, request)
        done = False
        while done is False:
            status, done = downloader.next_chunk()
            print(f"Download {int(status.progress() * 100)}%.", file=sys.stderr)

        # Write to stdout or file
        if output_path == "-":
            sys.stdout.buffer.write(fh.getvalue())
        else:
            with open(output_path, "wb") as f:
                f.write(fh.getvalue())
            print(f"CSV downloaded to {output_path}", file=sys.stderr)

    except HttpError as error:
        if error.resp.status == 404:
            print("\nERROR: File not found or not accessible (404).")
            print(
                "\nWARNING: Make sure the spreadsheet is shared with the service account email:"
            )
            print(f"         {service_account_email}")
            print("\nTo share the document:")
            print("1. Open the Google Sheet in your browser")
            print("2. Click the 'Share' button in the top-right corner")
            print("3. Enter the service account email address above")
            print("4. Make sure to give at least 'Viewer' access")
            print("5. Click 'Send' (no need to send the notification email)")
        else:
            print(f"An error occurred: {error}")


def main():
    parser = argparse.ArgumentParser(description="Download Google Sheets as CSV files")
    parser.add_argument("spreadsheet_id", help="The ID of the Google Sheet to download")
    parser.add_argument(
        "--key-file",
        "-k",
        required=True,
        help="Path to the service account key file (JSON)",
    )
    parser.add_argument(
        "--output",
        "-o",
        default="-",
        help="Output file path (use - for stdout, default: -)",
    )

    args = parser.parse_args()

    service_account_email = get_service_account_email(args.key_file)
    service, credentials = get_gdrive_service(args.key_file)
    download_sheet_as_csv(
        service, args.spreadsheet_id, args.output, service_account_email
    )


if __name__ == "__main__":
    main()
