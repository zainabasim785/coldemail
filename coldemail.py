import os
import json
import streamlit as st
from crewai import Agent, Task, Crew, Process, LLM
from crewai_tools import ScrapeWebsiteTool
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()

st.set_page_config(page_title="Cold Email Generator Pro", page_icon="📧", layout="wide")

if "history" not in st.session_state:
    st.session_state.history = []

st.title("📧 Cold Email Generator Pro")
st.markdown("AI-powered personalized cold emails with research & strategy")

tab1, tab2, tab3 = st.tabs(["🚀 Generate", "📜 History", "⚙️ Settings"])

with tab3:
    st.header("⚙️ AI Configuration")
    
    col1, col2 = st.columns(2)
    with col1:
        llm_provider = st.selectbox(
            "Provider",
            ["Groq", "Gemini", "OpenAI"],
            index=0
        )
    with col2:
        if llm_provider == "Groq":
            model = st.selectbox("Model", ["groq/llama-3.3-70b-versatile", "groq/llama3-8b-8192", "groq/mixtral-8x7b-32768"])
            api_key = os.getenv("GROQ_API_KEY")
        elif llm_provider == "Gemini":
            model = st.selectbox("Model", ["gemini/gemini-2.5-flash", "gemini/gemini-1.5-pro"])
            api_key = os.getenv("GEMINI_API_KEY")
        else:
            model = st.selectbox("Model", ["gpt-4", "gpt-3.5-turbo"])
            api_key = os.getenv("OPENAI_API_KEY")
    
    if not api_key:
        st.error(f"⚠️ {llm_provider.upper()}_API_KEY not set in .env")
    else:
        st.success(f"✅ {llm_provider} API key loaded")
    
    st.divider()
    st.header("🎨 Email Settings")
    
    email_tone = st.select_slider(
        "Email Tone",
        options=["Formal", "Professional", "Friendly", "Casual"],
        value="Professional"
    )
    
    email_length = st.slider("Max Words", 50, 300, 150)
    
    include_cta = st.checkbox("Include Call-to-Action", value=True)

with tab1:
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.header("🏢 Your Agency")
        
        your_name = st.text_input("Your Name", placeholder="John Doe")
        your_title = st.text_input("Your Title", placeholder="Founder & CEO")
        company_name = st.text_input("Your Company", placeholder="Acme Agency")
        
        agency_services = st.text_area(
            "Services You Offer",
            value="""1. SEO Optimization - Increase organic traffic and rankings
2. Custom Web Development - Modern, fast, responsive websites  
3. AI Automation - Automate repetitive business tasks""",
            height=120
        )
    
    with col2:
        st.header("🎯 Target Prospect")
        
        target_url = st.text_input("Company Website", placeholder="https://example.com")
        
        st.info("💡 The AI will research the company from their website")

    st.divider()
    
    if st.button("🚀 Generate Cold Email", type="primary", use_container_width=True):
        if not target_url:
            st.error("Please enter a target company URL")
        elif not api_key:
            st.error(f"Please set your {llm_provider.upper()}_API_KEY")
        elif not your_name or not company_name:
            st.error("Please fill in your name and company")
        else:
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            with st.spinner(""):
                try:
                    status_text.text("🔍 Researching company...")
                    progress_bar.progress(25)
                    
                    llm = LLM(model=model, api_key=api_key)
                    scrape_tool = ScrapeWebsiteTool()
                    
                    researcher = Agent(
                        role='Business Intelligence Analyst',
                        goal='Research company and identify pain points',
                        backstory="Expert at analyzing business websites to find opportunities.",
                        tools=[scrape_tool],
                        verbose=False,
                        llm=llm
                    )
                    
                    status_text.text("🎯 Matching services...")
                    progress_bar.progress(50)
                    
                    strategist = Agent(
                        role='Sales Strategist',
                        goal='Select best service to pitch',
                        backstory=f"Expert at matching services to client needs. Services: {agency_services}",
                        verbose=False,
                        llm=llm
                    )
                    
                    status_text.text("✍️ Writing email...")
                    progress_bar.progress(75)
                    
                    writer = Agent(
                        role='Senior Copywriter',
                        goal='Write compelling cold emails',
                        backstory=f"Expert copywriter. Tone: {email_tone}. Writes concise, persuasive emails under {email_length} words.",
                        verbose=False,
                        llm=llm
                    )
                    
                    tasks = [
                        Task(
                            description=f"Research {target_url}. What do they do? What are their pain points?",
                            expected_output="Company summary and 2-3 pain points.",
                            agent=researcher
                        ),
                        Task(
                            description=f"Pick ONE service from: {agency_services} that best solves their problem.",
                            expected_output="Selected service and why it's a match.",
                            agent=strategist
                        ),
                        Task(
                            description=f"""Write a {email_tone.lower()} cold email from {your_name} ({your_title}) at {company_name}.
                            To: CEO at target company
                            Mention specific findings from research.
                            Pitch the selected service.
                            {'Include a clear call-to-action.' if include_cta else ''}
                            Max {email_length} words. Make it personal and compelling.""",
                            expected_output="Professional cold email.",
                            agent=writer
                        )
                    ]
                    
                    crew = Crew(
                        agents=[researcher, strategist, writer],
                        tasks=tasks,
                        process=Process.sequential,
                        verbose=False
                    )
                    
                    result = crew.kickoff()
                    progress_bar.progress(100)
                    status_text.empty()
                    
                    st.success("✅ Email generated!")
                    
                    email_text = str(result)
                    
                    st.session_state.history.append({
                        "date": datetime.now().strftime("%Y-%m-%d %H:%M"),
                        "target": target_url,
                        "email": email_text
                    })
                    
                    st.markdown("### 📨 Your Cold Email")
                    st.markdown("---")
                    st.markdown(email_text)
                    st.markdown("---")
                    
                    col_dl, col_copy = st.columns(2)
                    with col_dl:
                        st.download_button(
                            "📥 Download",
                            email_text,
                            file_name=f"cold_email_{target_url.replace('https://', '').replace('/', '_')}.txt",
                            mime="text/plain",
                            use_container_width=True
                        )
                    with col_copy:
                        st.code(email_text, language="text")
                        
                except Exception as e:
                    st.error(f"❌ Error: {str(e)}")
                    progress_bar.empty()

with tab2:
    st.header("📜 Generated Emails History")
    
    if not st.session_state.history:
        st.info("No emails generated yet. Go to the Generate tab to create one!")
    else:
        for i, item in enumerate(reversed(st.session_state.history)):
            with st.expander(f"📧 {item['target']} - {item['date']}"):
                st.markdown(item['email'])
                if st.button(f"🗑️ Delete", key=f"del_{i}"):
                    st.session_state.history.remove(item)
                    st.rerun()

st.markdown("---")
st.markdown("Made with ❤️ using CrewAI & Streamlit")
