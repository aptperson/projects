import smtplib # smtplib and email are inherent to python3.10
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication

# used this guy's code: https://medium.com/@abdullahzulfiqar653/sending-emails-with-attachments-using-python-32b908909d73

# let's make this a function
def send_email_with(csv_file_path = "", body="typical message"):
    sender_email = "your@email"
    receiver_email = "also your@email" # you can use a list to email multiple accounts.
    password = "your email password" # Or an app-specific password for providers like Gmail
    subject = "Email with CSV Attachment"
    body = "Please find the attached CSV file."
    smtp_server = 'smtp.gmail.com'
    smtp_port = 465
    csv_file_path = csv_file_path#"./try_to_buy.csv"

    msg = MIMEMultipart()
    msg['From'] = sender_email
    msg['To'] = receiver_email
    msg['Subject'] = subject
    body_part = MIMEText(body)
    msg.attach(body_part)

    # section 1 to attach file
    with open(csv_file_path,'rb') as file:
        # Attach the file with filename to the email
        msg.attach(MIMEApplication(file.read(), Name="example.csv"))

    # section 2 for sending email
    with smtplib.SMTP_SSL(smtp_server, smtp_port) as server:
       server.login(sender_email, password)
       server.sendmail(sender_email, receiver_email, msg.as_string())
    return

