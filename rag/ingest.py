from rag.candidate_profile import load_candidate_profile
from rag.chroma import get_candidate_collection


def build_documents(profile):
    documents = []

    # ========================================================
    # WORK EXPERIENCE
    # ========================================================

    for index, experience in enumerate(profile.work):

        period = f"{experience.startDate} - " f"{experience.endDate or 'Heute'}"

        full_experience = "\n".join(
            [
                f"Company: {experience.company}",
                f"Position: {experience.position}",
                f"Location: {experience.location or ''}",
                f"Period: {period}",
                "",
                "Technologies:",
                ", ".join(experience.technologies),
                "",
                "Highlights:",
                *[f"- {item}" for item in experience.highlights],
            ]
        )

        documents.append(
            {
                "id": f"work_{index}",
                "document": full_experience,
                "metadata": {
                    "type": "work",
                    "company": experience.company,
                    "position": experience.position,
                    "start_date": experience.startDate,
                    "end_date": experience.endDate or "",
                },
            }
        )

        # ----------------------------------------------------
        # Individual work highlights
        # ----------------------------------------------------

        documents.extend(
            {
                "id": (f"work_{index}_highlight_" f"{bullet_index}"),
                "document": (
                    f"Company: {experience.company}\n"
                    f"Position: {experience.position}\n"
                    f"Highlight: {bullet}"
                ),
                "metadata": {
                    "type": "work_highlight",
                    "company": experience.company,
                    "position": experience.position,
                },
            }
            for bullet_index, bullet in enumerate(experience.highlights)
        )

    # ========================================================
    # PROJECTS
    # ========================================================

    for index, project in enumerate(profile.projects):

        period = f"{project.startDate} - " f"{project.endDate or 'Present'}"

        project_text = "\n".join(
            [
                f"Project: {project.name}",
                f"Period: {period}",
                f"Context: {project.context or ''}",
                "",
                "Technologies:",
                ", ".join(project.technologies),
                "",
                "Highlights:",
                *[f"- {item}" for item in project.highlights],
            ]
        )

        documents.append(
            {
                "id": f"project_{index}",
                "document": project_text,
                "metadata": {
                    "type": "project",
                    "project": project.name,
                    "start_date": project.startDate,
                    "end_date": project.endDate or "",
                },
            }
        )

        # ----------------------------------------------------
        # Individual project highlights
        # ----------------------------------------------------

        documents.extend(
            {
                "id": (f"project_{index}_highlight_" f"{bullet_index}"),
                "document": (f"Project: {project.name}\n" f"Highlight: {bullet}"),
                "metadata": {
                    "type": "project_highlight",
                    "project": project.name,
                },
            }
            for bullet_index, bullet in enumerate(project.highlights)
        )

    # ========================================================
    # CONFERENCES
    # ========================================================

    for index, conference in enumerate(profile.conferences):

        period = f"{conference.startDate} - " f"{conference.endDate or 'Present'}"

        conference_text = "\n".join(
            [
                f"Conference: {conference.title}",
                f"Period: {period}",
                f"Link: {conference.url or ''}",
                "",
                "Highlights:",
                *[f"- {item}" for item in conference.highlights],
            ]
        )

        documents.append(
            {
                "id": f"conference_{index}",
                "document": conference_text,
                "metadata": {
                    "type": "conference",
                    "title": conference.title,
                },
            }
        )

    # ========================================================
    # ACHIEVEMENTS
    # ========================================================

    documents.extend(
        {
            "id": f"achievement_{index}",
            "document": (
                f"Achievement: {achievement.title}\n" f"{achievement.description}"
            ),
            "metadata": {
                "type": "achievement",
                "title": achievement.title,
            },
        }
        for index, achievement in enumerate(profile.achievements)
    )

    # ========================================================
    # SKILLS
    # ========================================================

    if profile.skills:

        skills = profile.skills

        documents.append(
            {
                "id": "skills_technical",
                "document": "\n".join(
                    [
                        "Technical Skills",
                        "",
                        "Programming Languages:",
                        ", ".join(skills.programming_languages),
                        "",
                        "Frameworks and Libraries:",
                        ", ".join(skills.frameworks_libraries),
                        "",
                        "Development Tools and DevOps:",
                        ", ".join(skills.tools_devops),
                    ]
                ),
                "metadata": {
                    "type": "skills",
                },
            }
        )

    # ========================================================
    # LANGUAGES
    # ========================================================

    if profile.languages:

        language_text = "\n".join(
            [
                (f"- {language.language}: " f"{language.fluency}")
                for language in profile.languages
            ]
        )

        documents.append(
            {
                "id": "languages",
                "document": ("Languages:\n" + language_text),
                "metadata": {
                    "type": "languages",
                },
            }
        )

    return documents


def ingest_candidate_profile():

    profile = load_candidate_profile()

    collection = get_candidate_collection()

    documents = build_documents(profile)

    if not documents:
        raise RuntimeError("No candidate documents were generated.")

    collection.upsert(
        ids=[item["id"] for item in documents],
        documents=[item["document"] for item in documents],
        metadatas=[item["metadata"] for item in documents],
    )

    print(f"✅ Indexed {len(documents)} " "candidate documents.")


if __name__ == "__main__":
    ingest_candidate_profile()
