from crewai import Agent, Task,Crew,LLM
from crewai_tools import SerperDevTool
from dotenv import load_dotenv

import os 

load_dotenv()
search_tool = SerperDevTool()


llm = LLM(
    model = "gemini/gemini-2.5-flash",
    api_key = os.getenv("GEMINI_API_KEY")
)

researcher = Agent(
    role = "research assistant",
    goal = "find information about a topic",
    backstory = "you are a helpful research assistant ",
    llm=llm,
    tools=[search_tool]
)
    
research_task = Task(
    description= "search the web and find information about the sun",
    expected_output = "a summary of 3 line of the information on the web about the sun",
    agent=researcher
)
crew = Crew(
    agents=[researcher],
    tasks=[research_task],
    verbose=True 
)
result = crew.kickoff()
print(result)