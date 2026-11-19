from dotenv import load_dotenv
import os
load_dotenv()
from langchain.agents import create_agent
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from tools import web_scraper, web_search

llm = ChatGroq(
    model="openai/gpt-oss-20b",
    temperature=0,
    max_tokens=3000,
    reasoning_effort="low",
)

SEARCH_AGENT_PROMPT = """You are a research search assistant. Use the web_search tool to find recent, reliable information.

Return your findings as a markdown table with exactly these columns:
| Title | Key Finding | Source URL |

Rules:
- The Source URL column must contain the full, unmodified https:// link copied from the tool output.
- Never list a source without its URL.
- Only use information that appears in the tool output."""


def build_search_agent():
    agent = create_agent(
        model=llm,
        tools=[web_search],
        system_prompt=SEARCH_AGENT_PROMPT,
    )
    return agent

def build_scraper_agent():
    agent = create_agent(
        model=llm,
        tools=[web_scraper]
    )
    return agent

writer_prompt = ChatPromptTemplate.from_messages(
    [
        ('system', "You are an expert research writer. Write a detailed and well-structured article based on the information provided. Ensure clarity, cohesion, and depth in your writing."),
        ('human', """Write a detailed research report on the topic below:
Topic: {topic}
Research Gathered: {research}

Structure the report as :
    - Introduction
    - Key Findings (minimum 3 well-explained points)
    - Conclusion
    - Sources (List all the urls found in the research)
Be detailed, factual and professional.""")
    ]
)

writer_chain = writer_prompt | llm | StrOutputParser()

# Critic Chain with improved prompt
critic_prompt = ChatPromptTemplate.from_messages([
    ("system", "You are a sharp and constructive research critic. Be honest and specific."),
    ("human", """Review the research report below and evaluate it strictly.

Report:
{report}

If the report is missing major sections, give a minimum score of 5/10 and note the missing parts.
Respond in this exact format:
Score: X/10
Strengths:
    - ...
Areas to Improve:
    - ...
One line verdict:
    ...""")
])

critic_chain = critic_prompt | llm | StrOutputParser()