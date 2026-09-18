from langgraph.graph import StateGraph, START, END
from workflow.constants import Constants
from workflow.state import JobState
from workflow.nodes.analyze_job import analyze_job_node
from workflow.nodes.retrieve_context import retrieve_candidate_evidence
from workflow.nodes.tailor_resume import generate_tailored_resume
from workflow.nodes.generate_cover_letter import generate_cover_letter
from workflow.nodes.verify_output import verify_and_filter_analyzed_job
from workflow.nodes.research_company import research_company
from workflow.nodes.generate_pdf import generate_pdfs


def build_job_graph():

    builder = StateGraph(JobState)

    # --------------------------------------------------------
    # Nodes
    # --------------------------------------------------------

    builder.add_node("analyze_job", analyze_job_node)
    builder.add_node("retrieve_context", retrieve_candidate_evidence)
    builder.add_node("generate_cover_letter", generate_cover_letter)
    builder.add_node("generate_tailored_resume", generate_tailored_resume)
    builder.add_node("research_company", research_company)
    builder.add_node("generate_pdfs", generate_pdfs)

    # --------------------------------------------------------
    # Flow
    # --------------------------------------------------------

    builder.add_edge(START, "retrieve_context")
    builder.add_edge("retrieve_context", "analyze_job")
    builder.add_conditional_edges(
        "analyze_job",
        verify_and_filter_analyzed_job,
        {Constants.SUCCESS: "research_company", Constants.FAILURE: END},
    )
    builder.add_edge("research_company", "generate_tailored_resume")
    builder.add_edge("research_company", "generate_cover_letter")
    builder.add_edge("generate_tailored_resume", "generate_pdfs")
    builder.add_edge("generate_cover_letter", "generate_pdfs")
    builder.add_edge("generate_pdfs", END)

    return builder.compile()


if __name__ == "__main__":

    graph = build_job_graph()

    # state = JobState(
    #     job_url="https://www.infineon.com/cms/en/careers/job-working-student-ai-analog-design",
    #     company_name="Infineon Technologies",
    #     company_location="Munich, Germany",
    #     job_title="Working Student: AI & LLM Methods for Analog Circuit Design",
    #     job_description="""
    #             About the job:
    #             #WeAreIn to create tiny chips and big careers.

    #             Key responsibilities:
    #             - Literature Study: Review and compare recent AI- and LLM-based approaches for analog circuit sizing, optimization, and design-space exploration.
    #             - AI Method Development: Develop LLM-assisted methods for circuit topology understanding, result interpretation, device sizing, and design knowledge extraction.
    #             - Circuit Benchmarking: Validate own methods on analog circuit blocks and benchmark accuracy, robustness, and design effort against conventional optimization methods.
    #             - Documentation and Presentation: Document your methods, implementation, benchmark results, and limitations.

    #             Your profile:
    #             - Master's student in Electrical Engineering or Computer Engineering.
    #             - Basic knowledge/interest in AI-based engineering workflows (LLMs, agent-based methods).
    #             - Basic experience with analog circuit design, simulation, and circuit performance results.
    #             - Understanding of analog circuit trade-offs, device sizing principles, and design-space exploration.
    #             - Familiarity with Cadence design tools and Python.
    #             - Good English communication skills.
    #             - Part-time student regulations apply (max 20h/week during semester, living close to site).
    #             """,
    # )

    state = JobState(
        job_url="https://www.soprasteria.de/karriere/job-werkstudent-custom-software-solutions",
        company_name="Sopra Steria (Custom Software Solutions)",
        company_location="München, Germany",
        job_title="Werkstudent (m/w/d) Custom Software Solutions - GenAI & Web Development",
        job_description="""
Unternehmensbeschreibung:
Wir sind die Custom Software Solutions - eine Gemeinschaft von Tech-Enthusiast*innen bei Sopra Steria.

Stellenbeschreibung:
- Standort: München, Hamburg oder Karlsruhe.
- Mitarbeit an Themen der digitalen Transformation und der European Digital Identity (EUDI) Wallet.
- Einsatz moderner Technologien, Generativer KI und Agentic Coding (GitHub Copilot, Claude Code).
- Softwareentwicklung nach Clean Code Prinzipien mit Java/Python im Backend und React/Angular im Frontend.
- Mitgestaltung von UI/UX und Begeisterung für gutes Design.

Qualifikationen:
- Immatrikuliert im Bachelor/Master (Informatik, Wirtschaftsinformatik oder vergleichbar) für mind. 2 weitere Semester.
- Erfahrung im Web Development mit Java und/oder Python.
- Kenntnisse in React oder Angular von Vorteil.
- Offenheit für KI-Tools (GitHub Copilot, Claude Code) und souveräner Umgang damit.
- Sehr gute Deutschkenntnisse (mind. C1) sowie gute Englischkenntnisse.
- Arbeitszeit: 10–20 Std./Woche im Semester.
    """,
    )

    result = graph.invoke(state.model_dump())

    print(result)
