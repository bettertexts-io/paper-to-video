## Author: Dominik Scherm
## Objective: build a script based on a paper text

import os
from os.path import join, dirname
from dotenv import load_dotenv
from langchain import LLMChain, PromptTemplate
from langchain.chat_models import ChatOpenAI

# Dotenv setup
dotenv_path = join(dirname(__file__), '.env')
load_dotenv(dotenv_path)

os.environ["OPENAI_API_KEY"] = os.environ.get("OPENAI_API_KEY")

def text_to_script(input) -> str:
    """Converts a paper's text to a vid script."""

    print("Converting text to script...")

    template = 'Write a video script for a short, informative, scientific video based on this scientific paper: {input}. The optimum output should be around 1000 words.'
    prompt = PromptTemplate.from_template(template)

    llm = ChatOpenAI(model="gpt-4")
    llm_chain = LLMChain(prompt=prompt, llm=llm)

    print("Generating script...")

    result = llm_chain(inputs={input})

    return result["text"]


if __name__ == "__main__":
    # Read sample string from txt file
    with open("excerpt.txt", "r") as f:
        input = f.read()
        print(text_to_script(input))
