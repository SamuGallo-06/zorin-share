import os
from dataclasses import dataclass, field

@dataclass
class SharedFolder:
    comment: str = "Shared Folder"
    name: str = ""
    path: str = ""
    read_only: bool = False
    guest_ok: bool = False
    valid_users: list = field(default_factory=list)
    create_mask: str = "0777"
    directory_mask: str = "0777"
    browseable: bool = True
    writeable: bool = True 

@dataclass
class SharedPrinter:
    comment: str = "Shared Printer"
    name: str = ""
    path: str = ""
    read_only: bool = False
    guest_ok: bool = False
    valid_users: list = field(default_factory=list)


