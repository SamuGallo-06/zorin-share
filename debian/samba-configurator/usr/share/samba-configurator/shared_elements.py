import os
from dataclasses import dataclass, field
from i18n import _

@dataclass
class SharedFolder:
    comment: str = _("Shared Folder")
    name: str = ""
    path: str = ""
    read_only: bool = False
    guest_ok: bool = False
    valid_users: list = field(default_factory=list)
    create_mask: str = "0777"
    directory_mask: str = "0777"
    browseable: bool = True
    writeable: bool = True


