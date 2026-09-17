from rag.candidate_profile import load_candidate_profile


def test_candidate_profile_loads():

    profile = load_candidate_profile()

    assert profile.basics.name == "Jainish Parekh"

    assert len(profile.education) > 0

    assert len(profile.work) > 0

    assert len(profile.projects) > 0

    assert len(profile.conferences) > 0

    assert profile.skills is not None

    assert len(profile.languages) > 0
    

