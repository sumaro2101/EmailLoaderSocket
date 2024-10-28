import re


REGEX_TYPE_EMAILS = r"^(.+)@{1}(?:yandex\.ru|mail\.ru|gmail\.com)$"


def check_email_type(email: str) -> re.Match[str] | None:
    check = re.match(
        REGEX_TYPE_EMAILS, email,
        )
    return check
