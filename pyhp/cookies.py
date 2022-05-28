from typing import Optional, Union
from dataclasses import dataclass
from datetime import datetime, timedelta


@dataclass
class NewCookie:
    key: str
    value: str = ''
    max_age: Optional[Union[timedelta, int]] = None
    expires: Optional[Union[str, datetime, int, float]] = None
    path: Optional[str] = '/'
    domain: Optional[str] = None
    secure: bool = False
    httponly: bool = False
    samesite: Optional[str] = None


@dataclass
class DeleteCookie:
    key: str
    path: str = '/'
    domain: Optional[str] = None
    secure: bool = False
    httponly: bool = False
    samesite: Optional[str] = None
