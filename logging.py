from os import path
from datetime import datetime
from encryption import decrypt_data, encrypt_data

if __name__ == "__main__":
    raise SystemExit("This file is not meant to be run directly. Please run the main script called um_members.py")

HIDDEN_LOG = "_hidden"


class LogEntry:
    def __init__(self, id: str|int, date: str, time: str, username: str,
                 description: str, additional_info: str, suspicious: str):
        self.id: int = int(id)
        self.date: str = date
        self.time: str = time
        self.username: str = username
        self.description: str = description
        self.additional_info: str = additional_info
        self.suspicious: str = suspicious

    def to_string(self) -> str:
        return (f"{self.id};{self.date};{self.time};{self.username};{self.description};"
                f"{self.additional_info};{self.suspicious}")

    @classmethod
    def from_string(cls, string):
        return cls(*string.split(";"))


class Logger:
    """
    This class is responsible for logging all the actions that are happening in the system.
    It logs the date, time, username, description, additional info and if the action was suspicious or not.
    It also keeps track of the login attempts and password change attempts.
    """

    def __init__(self, path):
        self.path = path
        self.login_attempts = 0
        self.change_attempts = 0
        logs = self.get_all_logs()
        self.current_index = len(logs)

    def _get_logs(self) -> list[LogEntry]:
        logs = []

        if not path.exists(self.path):
            return logs

        with open(self.path, "rb") as file:
            while True:
                # we read the data in chunks of 256 bytes because the encrypted data is 256 bytes long
                encrypted_content = file.read(256)
                if not encrypted_content:
                    break
                content = decrypt_data(encrypted_content.hex())
                logs.append(LogEntry.from_string(content))

        return logs

    def _save_log(self, log) -> None:
        log_string = log.to_string()
        encrypted_content = encrypt_data(log_string)
        with open(self.path, "ab") as file:
            file.write(encrypted_content)

    def log(self, username, description, additional_info, suspicious) -> None:
        username = username.replace(';', ' ')
        description = description.replace(';', ' ')
        additional_info = additional_info.replace(';', ' ')
        self.current_index += 1
        new_log = LogEntry(self.current_index, str(datetime.now().date()),
                           str(datetime.now().time().strftime("%H:%M:%S")),
                           username, description, additional_info, suspicious)
        self._save_log(new_log)

    def flag_logs_as_viewed(self):
        hidden_log = LogEntry(self.current_index, str(datetime.now().date()),
                              str(datetime.now().time().strftime("%H:%M:%S")), "...",
                              HIDDEN_LOG, HIDDEN_LOG, False)
        self._save_log(hidden_log)

    def _get_lasted_viewed(self) -> LogEntry | None:
        last_viewed = [log for log in self._get_logs() if log.description == HIDDEN_LOG]
        if last_viewed:
            return last_viewed[-1]
        return None

    def new_risk_detected(self) -> bool:
        last_viewed = self._get_lasted_viewed()
        if not last_viewed:
            for log in self._get_logs():
                if log.suspicious == "True":
                    return True

        for log in self._get_logs():
            if log.id > last_viewed.id and log.suspicious == "True":
                return True

        return False

    def get_all_logs(self) -> list[LogEntry]:
        return [log for log in self._get_logs() if log.description != HIDDEN_LOG]

    def reset_fields(self) -> None:
        self.login_attempts = 0
        self.change_attempts = 0
