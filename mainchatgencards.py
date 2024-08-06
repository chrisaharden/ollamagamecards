
import ollama
import generate_card_pdf
import sys
from ollama import chat


def parse_config_file(file_path):
    config = {}
    with open(file_path, 'r') as file:
        for line in file:
            if ':' in line:
                key, value = line.split(':', 1)
                config[key.strip()] = value.strip()
    return config

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python script.py <config_file_path>")
        sys.exit(1)
    
    file_path = sys.argv[1]
    config = parse_config_file(file_path)
    for key, value in config.items():
        print(f"{key}: {value}")

    # use the Content Type to chose the right prompt
    bQuestions:bool = "question" in config.get('Content Type').lower()
    if bQuestions:
        systemPrompt: str = "Output questions as list with question marks at the end of each question."\
            "  Do not include any carriage returns"\
            "  Do not include any line feeds"\
            "  Example: How are you? What are you doing? What is that?"
    else:
        systemPrompt: str = "Output a comma separated list. "\
            "  Do not include any carriage returns"\
            "  Do not include any line feeds"\
            "  Example: boy, girl, dog"

    # Build a sentence that uses all the key value pairs in the Content description.  
    # We'll pass the other parameters to the PDF generator.
    userPrompt: str =   "List "+config.get('Content Length')+\
                    " unique " +config.get('Content')+\
                    ". no yapping."
    print(f"userPrompt: {userPrompt}")



    print(f"systemPrompt: {systemPrompt}")

    messages = [
    {
        'role': 'system',
        'content': systemPrompt
    },
    {
        'role': 'user',
        'content': userPrompt,
    },
    {
        'role':'assistant',
        'content': 'Here is the list:',
    }
    ]

#response = chat('mistral', messages=messages)
response = chat('llama3.1', messages=messages)
print(response['message']['content'])

# generate the cards
generate_card_pdf.generate_card_pdf(response['message']['content'], config.get('Content Title'), config.get('Title Font'), False) #TODO remove the bQuestion param 
