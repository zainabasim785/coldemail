import os
import streamlit as st
from crewai import Agent, Task, Crew, Process, LLM
from crewai_tools import ScrapeWebsiteTool
from dotenv import load_dotenv

load_dotenv()

st.set_page_config(page_title="Cold Email Generator", page_icon="📧", layout="wide")

st.title("📧 AI Cold Email Generator")
st.markdown("Generate personalized cold emails for any company using AI agents")

with st.sidebar:
    st.header("⚙️ Settings")
    
    llm_provider = st.selectbox(
        "Select AI Provider",
        ["Groq", "Gemini"],
        index=0
    )
    
    if llm_provider == "Groq":
        model = st.selectbox(
            "Model",
            ["groq/llama-3.3-70b-versatile", "groq/llama3-8b-8192"],
            index=0
        )
        api_key = os.getenv("GROQ_API_KEY")
    else:
        model = st.selectbox(
            "Model",
            ["gemini/gemini-2.5-flash", "gemini/gemini-1.5-pro"],
            index=0
        )
        api_key = os.getenv("GEMINI_API_KEY")
    
    if not api_key:
        st.error(f"⚠️ {llm_provider.upper()}_API_KEY not set")

st.header("🏢 Your Information")

your_name = st.text_input("Your Name", placeholder="John Doe")
your_title = st.text_input("Your Title", placeholder="Founder & CEO")
your_company = st.text_input("Your Company", placeholder="Acme Agency")

st.header("📋 Your Agency Services")
agency_services = st.text_area(
    "Describe your services",
    value="""1. SEO Optimization Service: Best for companies with good products but low traffic. We increase organic reach.
2. Custom Web Development: Best for companies with outdated, ugly, or slow websites. We build modern React/Python sites.
3. AI Automation: Best for companies with manual, repetitive tasks. We build agents to save time.""",
    height=150
)

st.header("🎯 Target Company")
target_url = st.text_input(
    "Company website URL",
    placeholder="https://example.com",
    value="https://github.com/"
)

def generate_cold_email(target_url, agency_services, your_name, your_title, your_company, model, api_key):
    llm = LLM(model=model, api_key=api_key)
    scrape_tool = ScrapeWebsiteTool()
    
    researcher = Agent(
        role='Business Intelligence Analyst',
        goal='Analyze the target company website and identify their core business and potential weaknesses.',
        backstory="You are an expert at analyzing businesses just by looking at their landing page.",
        tools=[scrape_tool],
        verbose=True,
        allow_delegation=True,
        memory=True,
        llm=llm
    )
    
    strategist = Agent(
        role='Agency Strategist',
        goal='Match the target company needs with ONE of our agency services.',
        backstory=f"""You work for a top-tier digital agency.
OUR SERVICES KNOWLEDGE BASE:
{agency_services}
You must pick the SINGLE best service for this specific client.""",
        verbose=True,
        memory=True,
        llm=llm
    )
    
    writer = Agent(
        role='Senior Sales Copywriter',
        goal='Write a personalized cold email that sounds human and professional.',
        backstory="You write emails that get replies. You never sound robotic.",
        verbose=True,
        llm=llm
    )
    
    task_analyze = Task(
        description=f"Scrape {target_url}. Summarize what they do and identify 1 key weakness.",
        expected_output="Brief summary and pain points.",
        agent=researcher
    )
    
    task_strategize = Task(
        description="Pick ONE service that solves their problem. Explain the match.",
        expected_output="Selected service and reasoning.",
        agent=strategist
    )
    
    task_write = Task(
        description=f"Draft a cold email to the CEO. {sender_info} Pitch the service. Under 150 words.",
        expected_output="Professional cold email.",
        agent=writer
    )
    
    crew = Crew(
        agents=[researcher, strategist, writer],
        tasks=[task_analyze, task_strategize, task_write],
        process=Process.sequential,
        verbose=True
    )
    
    return crew.kickoff()

if st.button("🚀 Generate Cold Email", type="primary", use_container_width=True):
    if not target_url:
        st.error("Please enter a company URL")
    elif not api_key:
        st.error(f"Please set your {llm_provider.upper()}_API_KEY in .env file")
    else:
        with st.spinner("🤖 AI agents are working..."):
            try:
                result = generate_cold_email(target_url, agency_services, your_name, your_title, your_company, model, api_key)
                
                st.success("✅ Cold email generated!")
                st.markdown("---")
                st.markdown(str(result))
                st.markdown("---")
                
                st.download_button(
                    label="📥 Download Email",
                    data=str(result),
                    file_name="cold_email.txt",
                    mime="text/plain"
                )
            except Exception as e:
                st.error(f"❌ Error: {str(e)}")

st.markdown("---")
st.markdown("Made with ❤️ using CrewAI and Streamlit")
