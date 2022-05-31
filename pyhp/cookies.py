"""
Sets up classes for storing information about cookies that will be created and
destroyed.
"""

# pylint: disable=too-many-instance-attributes

from typing import Optional, Union
from dataclasses import dataclass
from datetime import datetime, timedelta


@dataclass
class NewCookie:
    """Stores information about a cookie that will be created."""
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
    """Stores information about a cookie that will be destroyed."""
    key: str
    path: str = '/'
    domain: Optional[str] = None
    secure: bool = False
    httponly: bool = False
    samesite: Optional[str] = None
