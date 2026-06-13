import random

def get_random_security_tips():
    security_tips = [
        "Keep your software updated to protect against vulnerabilities.",
        "Use strong and unique passwords for each account.",
        "Enable two-factor authentication whenever possible.",
        "Regularly back up your data to prevent data loss in case of security breaches.",
        "Be cautious of phishing emails and never click on suspicious links or download attachments from unknown sources.",
        "Use a reputable antivirus software and keep it up to date.",
        "Avoid using public Wi-Fi networks for sensitive activities like online banking or shopping.",
        "Encrypt sensitive data to prevent unauthorized access."
    ]
    random.shuffle(security_tips)
    return security_tips[:5]
