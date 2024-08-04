import json
import ollama
import asyncio
import generate_card_pdf
import sys

# Updated function to generate a game PDF with an array of words and a title
def generate_pdf_carddeck(words: str, title: str) -> str:
    print(f"Title: {title}")
    print(f"Words: {words}")

    generate_card_pdf.generate_card_pdf(words, title)  # Assuming generate_card_pdf function is updated to accept title
    return json.dumps({"status": "PDF generated", "title": title, "words": words})

async def run(model: str, prompt:str):
    client = ollama.AsyncClient()
    # Initialize conversation with a user query
    messages = [{'role': 'user', 'content': prompt}]

    # First API call: Send the query and function description to the model
    response = await client.chat(
        model=model,
        messages=messages,
        tools=[
            {
                'type': 'function',
                'function': {
                    'name': 'generate_pdf_carddeck',
                    'description': 'Generate a PDF using the provided title and words',
                    'parameters': {
                        'type': 'object',
                        'properties': {
                            'title': {
                                'type': 'string',
                                'description': 'The title for the game',
                            },
                            'words': {
                                'type': 'string',
                                'description': 'A list of comma separated words to be used in the game',
                            },
                        },
                        'required': ['title', 'words'],
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
            function_args = tool['function']['arguments']
            function_response = function_to_call(function_args['words'], function_args['title'])
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

    # CH: use this in a python script for asynchronous processes:
    asyncio.run(run('llama3.1',prompt))

    # CH: Use this when you are in the jupyter notebook:
    # await run('llama3.1',argument_1)
    asyncio.run(run('llama3.1', prompt))
else:
    print("Error: Please provide a string as a command line argument, such as 'Can you generate a game pdf with a title and a comma separated list of 50 unique nouns?'.")