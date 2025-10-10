# app/config.py
from dataclasses import dataclass
from pathlib import Path

@dataclass(frozen=True)
class SeleniumConfig:
    user_data_dir: Path = Path(r"C:\SeleniumProfiles\SeleniumAirbus")
    profile_name: str = "Default"
    timeout_s: int = 20
    micro_wait_s: float = 0.25

@dataclass(frozen=True)
class CandidateData:
    semester_level: str = "M1"
    university: str = "UNIVERSITÉ TOULOUSE III - PAUL SABATIER"
    course: str = "Master’s In Computer Science for Aerospace"
    finish_studies: str = "06/24"
    availability: str = "1/1/2023 - 1/9/2023"
    duration: str = "Until 23/9/2023"
    birth_ddmmyyyy: str = "06101999"
    nationality: str = "Lebanon"
    english_level: str = "Negotiation / Fluent"
    french_level: str = "Intermediate"
