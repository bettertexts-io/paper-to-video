import os

from langchain.agents import AgentType, initialize_agent, load_tools
from langchain.chat_models import ChatOpenAI

from constants import OPENAI_API_KEY

os.environ["OPENAI_API_KEY"] = OPENAI_API_KEY

llm = ChatOpenAI(temperature=0)
tools = load_tools(
    ["arxiv"],
)

agent_chain = initialize_agent(
    tools,
    llm,
    agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
    verbose=True,
)

agent_chain.run(
    "Can you summarize arXiv:1706.03762 for an knowledge video?",
)

# Result: Could not find the papers I searched for in most of the cases
