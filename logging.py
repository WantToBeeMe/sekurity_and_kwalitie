from os import path
from datetime import datetime
from encryption import decrypt_data, encrypt_data

class LogEntry:
    def __init__(self, id, date, time, username, description, additional_info, suspicious):
        self.id = id
        self.date = date
        self.time = time
        self.username = username
        self.description = description
        self.additional_info = additional_info
        self.suspicious = suspicious

    def to_string(self):
        return f"{self.id};{self.date};{self.time};{self.username};{self.description};{self.additional_info};{self.suspicious}"

    def from_string(string):
        return LogEntry(*string.split(";"))

class Logger:
    def __init__(self, path):
        self.path = path
        self.login_attempts = 0
        self.change_attempts = 0
    def _get_logs(self):
        logs = []

        if not path.exists(self.path):
            return logs

        with open(self.path, "rb") as file:
            while True:
                encrypted_content = file.read(256)
                if not encrypted_content:
                    break
                content = decrypt_data(encrypted_content.hex())
                logs.append(LogEntry.from_string(content))

        return logs

    def _save_log(self, log):
        log_string = log.to_string()
        encrypted_content = encrypt_data(log_string)
        with open(self.path, "ab") as file:
            file.write(encrypted_content)

    def log(self, username, description, additional_info, suspicious):
        logs = self._get_logs()
        new_log = LogEntry(len(logs) + 1, str(datetime.now().date()), str(datetime.now().time().strftime("%H:%M:%S")), username, description, additional_info, suspicious)
        self._save_log(new_log)


    def get_recentlogs(self):
        logs = self._get_logs()
        return logs[-50:]


    def get_all_logs(self):
        return self._get_logs()


    def reset_fields(self):
        self.login_attempts = 0
        self.change_attempts = 0