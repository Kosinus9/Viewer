from dataclasses import dataclass

@dataclass
class ST_JobSection:
    file_name:  str
    file_path:  str
    section_id: str | None = None
