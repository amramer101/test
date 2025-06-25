from uuid import UUID
from dataclasses import dataclass
from typing import Optional
import datetime
from django.contrib.auth.hashers import check_password, make_password


@dataclass
class User:
    id: UUID
    username: str
    email: str
    hashed_password: str
    is_active: bool
    created_at: datetime.datetime
    updated_at: datetime.datetime

    def check_password(self, password: str) -> bool:
        return check_password(password, self.hashed_password)

    def set_password(self, password: str):
        self.hashed_password = make_password(password)

    def is_valid_email(self) -> bool:
        return "@" in self.email and "." in self.email
