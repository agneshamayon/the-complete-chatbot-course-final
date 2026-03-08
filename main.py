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

#chat_log = [{'role': 'system', 'content': 'you are a Python tutor, completely dedicated to teach users how to\
#                                         python from scratch.Please, give best practice'}]
"""
chat_log = [{'role': 'system', 'content': 'Au centre d’un domaine privé de plus de 100ha et bénéficiant d’une vue exceptionnelle sur les causses et la vallée de la Dourbie, cette grande demeure offre une totale tranquillité.'
                                          '7 Chambres - 4 parentales dont 2 de 30m2 avec grande terrasse et salles de bain en-suite et 1 de 40m2 et trois chambres d’enfants permettent d’accueillir jusqu’à 14 convives. Les salles communes comprennent un salon/cuisine/SAM de 50m2 et 2 salons séparés afin que chacun puisse profiter du séjour selon son humeur. 5 SDB dont 3 séparées et 6 WC (4 séparés), 1 buanderie / cellier. Des climatiseurs sont installés dans 2 salons et 6 chambres.'
                                          'L’extérieur est organisé pour le farniente et les activités sportives : Une grande piscine au sel chauffée de 6x12m avec ses transats, 1 terrain d’entrainement de basket (10x10m), 1 terrain de boules et une table de ping pong. Les amateurs de tennis pourront profiter du tennis municipal, gratuit et généralement libre, à proximité. Le GR passe devant la maison et il faut impérativement le suivre pour visiter le site classé de St Véran (45mn aller) ou de Roquesaltes (2h aller).'
                                          'Le domaine est situé sur les hauteurs de la vallée de la Dourbie dans le site des grands causses, site classé au patrimoine mondial de l’Unesco. Le domaine se trouve à 20km de Millau et de la A75.'
                                          'C’est un endroit idéal pour les vacances en famille ou en petit groupe, pour les amoureux des sports, de la nature et de la culture- cités et bastides templières et hospitalières, grottes et avens exceptionnels, le chaos de Montpellier le vieux et le site archéologique de la Graufesenque, et bien sur le viaduc.'
                                          'Chaque saison offre ses particularités. En hiver ski de fond à 40km au mont Aigoual et les nuits noires étoilées et la gastronomie de la truffe, printemps et automne pour les grandes promenades, les déjeuners au soleil et les soirées au coin de la cheminée;'
                                          'Ce domaine c’est l’espace, la sérénité, la liberté des petits et des grands dans un espace convivial et confortable.'
                                          'Les équipements sont Piscine, Basket, terrain de boule,Lave-linge,Sèche-linge,Animaux de compagnie admis,Wi-Fi gratuit.'
                                          'Donne une réponse concise et courte avec des mots sans cesure'}]
"""

chat_log = [{'role': 'system', 'content': 'Large Comfortable Residence in a Private Estate with Pool and Breathtaking Views'
                                          'Set in the heart of a private estate of over 100 hectares and enjoying exceptional views over the "Causses plateaux" and the "Dourbie Valley", this large residence offers complete tranquility.'
                                          '7 bedrooms – including 4 master suites (two of 30 m² with large terraces and en-suite bathrooms, and one of 40 m²), plus three children’s bedrooms – allow accommodation for up to 14 guests.'
                                          'The common areas include a 50 m² living room / kitchen / dining area and two additional separate lounges, so everyone can enjoy the stay according to their mood.'
                                          'There are 5 bathrooms (including 3 separate), 6 toilets (4 separate), and 1 laundry / pantry room.'
                                          'Air conditioning units are installed in 2 living rooms and 6 bedrooms.'
                                          'The outdoor area is designed for both relaxation and sports activities:'
                                          'A large heated saltwater swimming pool (6 × 12 m) with sun loungers'
                                          'A basketball practice court (10 × 10 m), A boules court , A ping-pong table'
                                          'Tennis enthusiasts can enjoy the nearby municipal tennis court, which is free and generally available.'
                                          'A GR hiking trail passes directly in front of the house and must be followed to visit the listed site of Saint-Véran (45 minutes one way) or Roquesaltes (2 hours one way).'
                                          'The estate is located on the heights of the Dourbie Valley, within the "Grands Causses", a UNESCO World Heritage Site. It lies 20 km from Millau and the A75 motorway.'
                                          'It is an ideal place for family holidays or small groups, for lovers of sports, nature, and culture: Templar and Hospitaller towns and bastides, spectacular caves and sinkholes, the rock formations of "Montpellier-le-Vieux", the archaeological site of "La Graufesenque", and of course the famous viaduc.'
                                          'Each season has its own charm. In winter, cross-country skiing at "Mont Aigoual" (40 km away), dark starry nights, and truffle gastronomy; spring and autumn are perfect for long walks, sunny lunches, and evenings by the fireplace.'
                                          'This estate offers space, serenity, and freedom for both children and adults, in a friendly and comfortable setting.'
                                          'Give a precise and short answer'}]
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
                    ai_response += chunk.choices[0].delta.content.strip()
                    await websocket.send_text(chunk.choices[0].delta.content.strip())
            chat_responses.append(ai_response)
            print('ai:  ', ai_response)
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
    print('xxxxxxxxxxxxxxxxxx  ', bot_response)
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
