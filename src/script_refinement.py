import time
from chroma import query_chroma_by_prompt

def generate_script(barebone_script_json: dict):
    """
    Given the summary of the paper, generate a detailed video script.
    This function queries the chroma vector database for each section to generate a script for a video.
    """

    script = []

    # Load json and iterate over each section
    sections = barebone_script_json["sections"]

    for section in sections:
        context = section["context"]

        # Frame the question to chroma to get video-friendly content
        section_prompt = f"Based on the following information:\n\n{context}\n\nCan you generate a script fit for a video presentation."

        section_script = query_chroma_by_prompt(section_prompt)

        # Check if chroma's response indicates a lack of information
        if "does not provide information" in section_script:
            section_script = f"Unfortunately, we couldn't generate a detailed video script based on the provided context. Further research or a different source might be required."

        script.append(section_script)

        # Sleep for 15 seconds between requests
        time.sleep(15)

    return script


def enrich_script_with_resources(section_script: list):
    enriched_scripts = []
    
    for script in section_script:
        # For simplicity, let's assume chroma also has access to relevant resources.
        resource_prompt = f"Based on the content:\n\n{script}\n\nCan you suggest visual resources or cues to enhance this section for a video presentation?"
        suggested_resources = query_chroma_by_prompt(resource_prompt)
        
        enriched_section = {
            "script": script,
            "resources": suggested_resources
        }
        
        enriched_scripts.append(enriched_section)
        time.sleep(15)  # Sleep for 15 seconds between requests
    
    return enriched_scripts



if __name__ == "__main__":
    # Read sample string from txt file

    print("generate_script")
        