import json
import ollama
import asyncio
import generate_card_pdf
import sys

# Updated function to generate a game PDF with an array of words, a title, a font, and a boolean for questions
def generate_pdf_carddeck(words: str, title: str, font: str, bQuestions: bool) -> str:
    print(f"Title: {title}")
    print(f"Words: {words}")
    print(f"Font: {font}")
    print(f"Include Questions: {bQuestions}")

    generate_card_pdf.generate_card_pdf(words, title, font, bQuestions)  # Assuming generate_card_pdf function is updated to accept bQuestions
    return json.dumps({"status": "PDF generated", "title": title, "words": words, "font": font, "bQuestions": bQuestions})

async def run(model: str, prompt:str):
    client = ollama.AsyncClient()

    #refine the prompt to ensure the model doesn't put extra phrases, "etc.", or extra items in the word and question list.
    #prompt = prompt+".  " 

    # Initialize conversation with a user query
    system_prompt = "You are acting as a tool to generate a PDF. You must generate the entire list of items before calling any tools."
    messages = [
        {
            'role': 'system', 
            'content': system_prompt
        },        
        {
            'role': 'user', 
            'content': prompt
        },
    ]

    # First API call: Send the query and function description to the model
    response = await client.chat(
        model=model,
        messages=messages,
        tools=[
            {
                'type': 'function',
                'function': {
                    'name': 'generate_pdf_carddeck',
                    'description': 'Generate a PDF using the provided title, words, font, and whether to include questions',
                    'parameters': {
                        'type': 'object',
                        'properties': {
                            'title': {
                                'type': 'string',
                                'description': 'The title for the PDF',
                            },
                            'words': {
                                'type': 'string',
                                'description': 'A list of comma separated words or questions to be used in the PDF',
                            },
                            'font': {
                                'type': 'string',
                                'description': 'The font to be used in the PDF',
                            },
                            'bQuestions': {
                                'type': 'boolean',
                                'description': 'Whether nouns or questions are being used in the PDF',
                            },
                        },
                        'required': ['title', 'words', 'font', 'bQuestions'],
                    },
                },
            },
        ],
    )

    # Add the model's response to the conversation history
    messages.append(response['message'])

    # Check if the model decided to use the provided function
    if not response['message'].get('tool_calls'):
        print("The model didn't use the function. Its response was:")
        print(response['message']['content'])
        return

    # Process function calls made by the model
    if response['message'].get('tool_calls'):
        available_functions = {
            'generate_pdf_carddeck': generate_pdf_carddeck,
        }
        for tool in response['message']['tool_calls']:
            function_to_call = available_functions[tool['function']['name']]
            function_args =  tool['function']['arguments']
            function_response = function_to_call(
                function_args['words'],
                function_args['title'],
                function_args['font'],
                function_args['bQuestions']
            )
            # Add function response to the conversation
            messages.append(
                {
                    'role': 'tool',
                    'content': function_response,
                }
            )

    # Second API call: Get final response from the model
    final_response = await client.chat(model=model, messages=messages)
    print(final_response['message']['content'])


# Run the async function
# asyncio.run(run('mistral'))
# asyncio.run(run('llama3.1'))

#MAIN CALL FROM THE COMMAND LINE
# Get the string from command line arguments (assuming the first argument is the text)
if len(sys.argv) > 1:
    prompt = sys.argv[1]

    # CH: Use this when you are in the jupyter notebook:
    # await run('llama3.1',argument_1)
    asyncio.run(run('llama3.1', prompt))
else:
    print("Error: Please provide a string as a command line argument, such as 'Generate a pdf card deck with 50 unique verbs with a title of Verbs and use Comic Sans MS font'.  You can also specify questions insetead of single words.")