import csv
import os
from datetime import date
from dotenv import load_dotenv
from PIL import Image

from certificate import create_certificate
from email_sender import send_email

def main():
    # Load variables from .env file
    load_dotenv()
    
    print("AWS SBG Certificate Dispatcher")
    print("1. Test (don't mail just show certificate)")
    print("2. Send all")
    choice = input("Enter your choice (1/2): ")
    
    if choice not in ['1', '2']:
        print("Invalid choice.")
        return
        
    if not os.path.exists("data.csv"):
        print("Error: data.csv not found. Please create data.csv with 'name' and 'email' columns.")
        return
        
    if not os.path.exists("body.html"):
        print("Error: body.html not found.")
        return
        
    with open("body.html", "r", encoding="utf-8") as f:
        html_template = f.read()
        
    with open("data.csv", "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        if 'name' not in reader.fieldnames or 'email' not in reader.fieldnames:
             print("Error: data.csv must contain 'name' and 'email' columns.")
             return
        data = list(reader)
        
    if choice == '1':
        if not data:
            print("No data in data.csv")
            return
        test_user = data[0]
        name = test_user.get('name', 'Test Name')
        print(f"Generating test certificate for: {name}")
        
        output_dir = "certificates/test"
        os.makedirs(output_dir, exist_ok=True)
        output_path = os.path.join(output_dir, f"test_certificate_{name.replace(' ', '_')}.png")
        if create_certificate(name, output_path=output_path):
            img = Image.open(output_path)
            img.show()
            print("Test certificate generated and displayed.")
            print(f"Saved locally as {output_path}")
            
    elif choice == '2':
        # Fetch from environment instead of prompting
        sender_email = os.getenv("GMAIL_USER")
        sender_password = os.getenv("GMAIL_APP_PASSWORD")
        sender_name = os.getenv("SENDER_NAME", "Prakhar Doneria")
        subject = os.getenv("DEFAULT_SUBJECT", "AWS Cloud & DSA Coding Challenge 2026 Certificate")
        
        if not sender_email or not sender_password:
            print("Error: GMAIL_USER and GMAIL_APP_PASSWORD must be set in .env file.")
            return
            
        print(f"\nUsing Sender: {sender_name} <{sender_email}>")
        print(f"Subject: {subject}")
        print("\nStarting dispatch...")
        
        for row in data:
            name = row.get('name')
            email = row.get('email')
            
            if not name or not email:
                print(f"Skipping row missing name or email: {row}")
                continue
                
            print(f"\nProcessing certificate for {name} ({email})...")
            
            dispatch_dir = "certificates/dispatch"
            os.makedirs(dispatch_dir, exist_ok=True)
            cert_path = os.path.join(dispatch_dir, f"{name.replace(' ', '_')}_certificate.png")
            
            if create_certificate(name, output_path=cert_path):
                # Replace placeholders in HTML
                first_name = name.split()[0] if name else ""
                html_content = html_template.replace("{{full_name}}", name)
                html_content = html_content.replace("{{first_name}}", first_name)
                html_content = html_content.replace("{{event_name}}", "AWS Cloud & DSA Coding Challenge 2026")
                html_content = html_content.replace("{{issue_date}}", date.today().strftime("%B %d, %Y"))
                
                print(f"Sending email to {email}...")
                success = send_email(sender_email, sender_password, sender_name, email, subject, html_content, cert_path)
                
                if success:
                    print(f"Successfully sent to {email}")
                else:
                    print(f"Failed to send to {email}")
                    
        print("\nDispatch complete!")

if __name__ == "__main__":
    main()
