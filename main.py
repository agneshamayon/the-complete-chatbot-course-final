from openai import OpenAI
from fastapi import FastAPI, Form, Request, WebSocket
from typing import Annotated
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
import os
from dotenv import load_dotenv

load_dotenv()

openai = OpenAI(
    api_key = os.getenv('OPENAI_API_SECRET_KEY')
)
app = FastAPI()

templates = Jinja2Templates(directory='templates')

chat_responses = []

@app.get("/", response_class=HTMLResponse)
async def chat_page(request: Request):
    return templates.TemplateResponse("home.html", {"request":request, "chat_responses":chat_responses})

chat_log = [{'role': 'system', 'content': 'you are a Python tutor, completely dedicated to teach users how to\
                                          python from scratch.Please, give best practice'}]


#server connection
@app.websocket("/ws")
async def chat(websocket: WebSocket):
    await websocket.accept()
    while True:
        user_input = await websocket.receive_text()
        chat_log.append({'role': 'user', 'content': user_input})
        chat_responses.append(user_input)
        try:
            response = openai.chat.completions.create(
                model='gpt-3.5-turbo',
                messages=chat_log,
                temperature=.6,
                stream =True
            )

            #bot_response = response.choices[0].message.content
            #await websocket.send_text(bot_response)
            ai_response = ''
            for chunk in response:
                if chunk.choices[0].delta.content is not None:
                    ai_response += chunk.choices[0].delta.content
                    await websocket.send_text(chunk.choices[0].delta.content)
            chat_responses.append(ai_response)

        except Exception as e:
            await websocket.send_text(f"Error: {str(e)}")
            break



@app.post("/", response_class=HTMLResponse)
async def chat(request: Request, user_input: Annotated[str,Form()]):
    chat_log.append({'role' : 'user', 'content': user_input})
    chat_responses.append(user_input)

    response = openai.chat.completions.create(
        model='gpt-3.5-turbo',
        messages=chat_log,
        temperature = .6)

    bot_response = response.choices[0].message.content
    chat_log.append({'role' : 'assistant', 'content': bot_response})
    chat_responses.append(bot_response)
    return templates.TemplateResponse("home.html", {'request': request, "chat_responses": chat_responses})


@app.get("/image", response_class=HTMLResponse)
async def image_page(request: Request):
    return templates.TemplateResponse("image.html", {"request":request})


@app.post("/image", response_class=HTMLResponse)
async def create_image(request: Request, user_input: Annotated[str,Form()]):
    response = openai.images.generate(
        prompt=user_input,
        n=1,
        size="256x256"
    )
    image_url = response.data[0].url
    return templates.TemplateResponse("image.html", {'request': request, "image_url": image_url})

    # Get base64 image
    #image_base64 = response.data[0].b64_json
    # Decode
    #image_bytes = base64.b64decode(image_base64)

    #return templates.TemplateResponse("image.html", {'request': request, "image_url": image_bytes})


"""
response = openai.chat.completions.create(
    model = 'gpt-3.5-turbo',
    messages = [{
        'role' : 'system',
        'content':'you are a helpful assistant.'
    },
        {'role' : 'user',
         'content': 'who won the six nations in 2020?'}]
)
response = openai.chat.completions.create(
    model = 'gpt-3.5-turbo',
    messages = [{
        'role' : 'system',
        'content':'you are a helpful assistant.'
        # 'content':'you are CEO of Apple'
    },
        {'role' : 'assistant',
         'content': 'Wales won the six nations in 2020?'} ,
        {'role' : 'user',
         'content': 'who was on the team?'}],
    temperature=.6
)

#print(response)
print(response.choices[0].message.content)
"""

"""
chat_log = []

while True:
    user_input = input()
    if user_input.lower() == 'stop':
        break
    chat_log.append({'role' : 'user', 'content': user_input})
    response = openai.chat.completions.create(
        model='gpt-3.5-turbo',
        messages=chat_log,
        temperature = .6)

    bot_response = response.choices[0].message.content
    chat_log.append({'role' : 'assistant', 'content': bot_response})
    print(bot_response)
"""
