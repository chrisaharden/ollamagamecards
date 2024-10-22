#This is an example that uses the websockets api to know when a prompt execution is done
#Once the prompt execution is done it downloads the images using the /history endpoint

import websocket #NOTE: websocket-client (https://github.com/websocket-client/websocket-client)
import uuid
import json
import urllib.request
import urllib.parse
import random
import os

server_address = "127.0.0.1:8188"
client_id = str(uuid.uuid4())

def queue_prompt(prompt):
    p = {"prompt": prompt, "client_id": client_id}
    data = json.dumps(p).encode('utf-8')
    req =  urllib.request.Request("http://{}/prompt".format(server_address), data=data)
    return json.loads(urllib.request.urlopen(req).read())

def get_image(filename, subfolder, folder_type):
    data = {"filename": filename, "subfolder": subfolder, "type": folder_type}
    url_values = urllib.parse.urlencode(data)
    with urllib.request.urlopen("http://{}/view?{}".format(server_address, url_values)) as response:
        return response.read()

def get_history(prompt_id):
    with urllib.request.urlopen("http://{}/history/{}".format(server_address, prompt_id)) as response:
        return json.loads(response.read())
    
def load_art_style(file_path):
    try:
        with open(file_path, 'r') as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading art style file: {e}")
        return None

def get_images(ws, prompt):
    prompt_id = queue_prompt(prompt)['prompt_id']
    output_images = {}
    while True:
        out = ws.recv()
        if isinstance(out, str):
            message = json.loads(out)
            if message['type'] == 'executing':
                data = message['data']
                if data['node'] is None and data['prompt_id'] == prompt_id:
                    break #Execution is done
        else:
            continue #previews are binary data

    history = get_history(prompt_id)[prompt_id]
    for o in history['outputs']:
        for node_id in history['outputs']:
            node_output = history['outputs'][node_id]
            if 'images' in node_output:
                images_output = []
                for image in node_output['images']:
                    image_data = get_image(image['filename'], image['subfolder'], image['type'])
                    images_output.append(image_data)
            output_images[node_id] = images_output

    return output_images

prompt_text = """
{
    "3": {
        "class_type": "KSampler",
        "inputs": {
            "cfg": 7,
            "denoise": 1,
            "latent_image": [
                "5",
                0
            ],
            "model": [
                "4",
                0
            ],
            "negative": [
                "7",
                0
            ],
            "positive": [
                "6",
                0
            ],
            "sampler_name": "euler_ancestral",
            "scheduler": "normal",
            "seed": 1050497315502915,
            "steps": 60
        }
    },
    "4": {
        "class_type": "CheckpointLoaderSimple",
        "inputs": {
            "ckpt_name": "sd_xl_base_1.0.safetensors"
        }
    },
    "5": {
        "class_type": "EmptyLatentImage",
        "inputs": {
            "batch_size": 1,
            "height": 904,
            "width": 904
        }
    },
    "6": {
        "class_type": "CLIPTextEncode",
        "inputs": {
            "clip": [
                "4",
                1
            ],
            "text": "masterpiece best quality"
        }
    },
    "7": {
        "class_type": "CLIPTextEncode",
        "inputs": {
            "clip": [
                "4",
                1
            ],
            "text": "bad hands"
        }
    },
    "8": {
        "class_type": "VAEDecode",
        "inputs": {
            "samples": [
                "3",
                0
            ],
            "vae": [
                "4",
                2
            ]
        }
    },
    "9": {
        "class_type": "SaveImage",
        "inputs": {
            "filename_prefix": "ComfyUI",
            "images": [
                "8",
                0
            ]
        }
    }
}
"""
def gen_image(subject:str, imageFileTitle:str, art_style_file:str=''):
    
    #load the comfyui prompt from the style file, or use the default
    if art_style_file and os.path.exists(art_style_file):
        prompt = load_art_style(art_style_file)
        if prompt is None:
            prompt = json.loads(prompt_text)
    else:
        prompt = json.loads(prompt_text)
    
    #set the text prompt for our positive CLIPTextEncode
    #append the subject from the user file to the comfyui prompt in the art_style file 
    existing_text = prompt["6"]["inputs"]["text"]
    prompt["6"]["inputs"]["text"] = f"{existing_text} of {subject}"

    #set the seed for our KSampler node
    seed = random.randint(1, 1000000)
    print(f"Generated seed: {seed}")
    prompt["3"]["inputs"]["seed"] = seed

    ws = websocket.WebSocket()
    ws.connect("ws://{}/ws?clientId={}".format(server_address, client_id))
    images = get_images(ws, prompt)

    #Commented out code to display the output images:
    #for node_id in images:
    #    for image_data in images[node_id]:
    #        from PIL import Image
    #        import io
    #        image = Image.open(io.BytesIO(image_data))
    #        image.show()

    # Save the image and return the filename
    for node_id in images:
        for i, image_data in enumerate(images[node_id]):
            from PIL import Image
            import io
            image = Image.open(io.BytesIO(image_data))
            filename = f".\\source\\images\\generatedimage_{imageFileTitle}_{node_id}_{i}.png"
            image.save(filename)
            print(f"Saved {filename}")
    return filename
