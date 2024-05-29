import os
import pickle
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from base64 import urlsafe_b64encode
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.image import MIMEImage

SCOPES = ["https://www.googleapis.com/auth/gmail.send"]

def authenticate():
    ''' Authenticate user to the Gmail API. '''
    creds = None

    # Absolute path to the credentials file
    base_dir = r'C:\Users\USER\Documents\Cyber Projects\1. Keylogger'
    credentials_path = os.path.join(base_dir, 'credentials.json')

    # Change working directory to base directory
    os.chdir(base_dir)
    
    # Debugging: print paths and directory contents
    print(f"Credentials path: {credentials_path}")
    print(f"Current working directory: {os.getcwd()}")
    print(f"Contents of directory: {os.listdir(base_dir)}")

    # Check if token.pickle exists (stores user's access and refresh tokens)
    if os.path.exists("token.pickle"):
        with open("token.pickle", "rb") as token:
            creds = pickle.load(token)

    # If there are no valid credentials, authenticate again
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            # Verify if the credentials file exists
            if not os.path.exists(credentials_path):
                print(f"File not found: {credentials_path}")
                raise FileNotFoundError(f"No such file or directory: '{credentials_path}'")

            flow = InstalledAppFlow.from_client_secrets_file(credentials_path, SCOPES)
            creds = flow.run_local_server(port=0)

        # Save the credentials for future use
        with open("token.pickle", "wb") as token:
            pickle.dump(creds, token)

    return build("gmail", "v1", credentials=creds)

service = authenticate()

def create_email_with_embedded_image(sender, to, subject, message_text, image_filename):
    ''' Create an email containing an embedded image. '''

    # Set up the email message
    msg = MIMEMultipart()
    msg["to"] = to
    msg["from"] = sender
    msg["subject"] = subject

    # Create HTML body with embedded image
    html = f"""\
    <html>
    <body>
        <img src="cid:image1" width="200" height="200">
        <p>{message_text}</p>
    </body>
    </html>
    """

    msg.attach(MIMEText(html, "html"))

    # Attach the image with a Content-ID
    with open(image_filename, "rb") as image_file:
        image_data = image_file.read()
        image = MIMEImage(image_data)
        image.add_header("Content-ID", "<image1>")
        msg.attach(image)

    return msg

def create_raw_email_message(message):
    ''' Convert the MIME message to a raw email message. '''
    return {"raw": urlsafe_b64encode(message.as_bytes()).decode()}

def send_email_with_embedded_image(sender, to, subject, message_text, image_filename):
    ''' Send an email with an embedded image using Gmail API. '''
    service = authenticate()

    # Create the email with the embedded image
    email_message = create_email_with_embedded_image(
        sender, to, subject, message_text, image_filename
    )

    # Convert to raw email message
    raw_email_message = create_raw_email_message(email_message)

    # Attempt to send the email
    try:
        message = (
            service.users()
            .messages()
            .send(userId="me", body=raw_email_message)
            .execute()
        )
        print("Message Id: %s" % message["id"])
        return message
    except Exception as error:
        print("An error occurred: %s" % error)
        return None
