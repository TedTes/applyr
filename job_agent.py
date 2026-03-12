from crewai import Agent, Task, Crew, Process
from langchain_community.tools import TavilySearchResults
from langchain_community.tools.playwright import NavigateTool, ClickTool, ExtractTextTool, FillTool, SubmitTool  # Browser tools
from playwright.sync_api import sync_playwright

# Tools
search_tool = TavilySearchResults(max_results=10)
browser_tools = [NavigateTool(), ClickTool(), ExtractTextTool(), FillTool(), SubmitTool()]  # Add more as needed

# Agents
searcher = Agent(
    role='Job Searcher',
    goal='Find relevant job listings based on criteria',
    backstory='You are an expert at querying job sites for software engineering roles in Toronto or remote.',
    tools=[search_tool],
    verbose=True
)

qualifier = Agent(
    role='Job Qualifier',
    goal='Score job fits and filter top ones',
    backstory='You evaluate jobs on skills match, salary, company rating. Score 1-10, pick top 3.',
    verbose=True
)

applier = Agent(
    role='Job Applier',
    goal='Draft cover letters and submit applications',
    backstory='You customize applications based on job desc and user resume. Use browser to fill forms.',
    tools=browser_tools,
    verbose=True
)

# Tasks
search_task = Task(
    description='Search for software engineering jobs in Toronto with keywords: {keywords}. Location: {location}. Return top 10 URLs and summaries.',
    agent=searcher,
    expected_output='List of job URLs with brief summaries'
)

qualify_task = Task(
    description='From {search_results}, score each on fit to resume: {resume_summary}. Pick top 3 with reasons.',
    agent=qualifier,
    expected_output='Top 3 jobs with scores and reasons'
)

apply_task = Task(
    description='For each top job {qualified_jobs}, draft a cover letter based on {resume_summary}. Navigate to URL, fill form if possible, or output draft for manual submit.',
    agent=applier,
    expected_output='Drafts and submission status'
)

# Crew
crew = Crew(
    agents=[searcher, qualifier, applier],
    tasks=[search_task, qualify_task, apply_task],
    process=Process.sequential,  # Or hierarchical for more control
    verbose=2
)

# Run it
inputs = {
    'keywords': 'software engineer python ai',
    'location': 'Toronto or remote',
    'resume_summary': 'Experienced SWE in Python, AI agents, Toronto-based.' 
}
result = crew.kickoff(inputs=inputs)
print(result)