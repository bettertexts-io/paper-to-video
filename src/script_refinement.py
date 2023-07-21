
from chroma import query_chroma_by_prompt


def generate_script(barebone_script_json: dict):
    """
    Given the summary of the paper, generate a basic video script.
    This function involves splitting the sections into chunks and querying the 
    chroma vector database for each section. The result is a script for a video
    """

    script = []
    
    # load json and iterate over each section
    sections = barebone_script_json["sections"]

    for section in sections:
        # Query your database here
        title = section["title"]
        context = section["context"]

        section_prompt = """Write a script for a video about the following section of the paper:

        Title:
        {title}

        Context:
        {context}

        Be as precise as possible.
        """

        section_script = query_chroma_by_prompt(section_prompt.format(title=title, context=context))
        print(section_script)

        script.append(section_script)

        return section_script


    return script


if __name__ == "__main__":
    # Read sample string from txt file

    print("generate_script")
        