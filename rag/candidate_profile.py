import json
from pathlib import Path
from schemas.candidate_profile import CandidateProfile


PROJECT_ROOT = Path(__file__).resolve().parents[1]

CANDIDATE_PROFILE_PATH = (
    PROJECT_ROOT
    / "data"
    / "candidate_profile.json"
)


def load_candidate_profile() -> CandidateProfile:

    with open(
        CANDIDATE_PROFILE_PATH,
        "r",
        encoding="utf-8"
    ) as file:

        data = json.load(file)

    return CandidateProfile.model_validate(data)