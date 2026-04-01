from openai import OpenAI
from fastapi import FastAPI, Form, Request, WebSocket
from typing import Annotated
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
import os
from dotenv import load_dotenv

from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_community.vectorstores import Chroma
from langchain_core.documents import Document

load_dotenv()
secret_key = os.getenv('OPENAI_API_SECRET_KEY')
openai = OpenAI(
    api_key = secret_key
)
app = FastAPI()

loader = PyPDFLoader("C:\ChatBot Tutorial\OpenAI\static/User_manual_Costeplane_march_28.pdf")
documents = loader.load()

summary = "".join(['Large Comfortable peaceful Residence in a Private Estate  of over 100 hectares with Pool.',
                    'Breathtaking Views over the Causses plateaux and the Dourbie Valley.',
                    '7 bedrooms – including 4 master suites (two of 30 m² with large terraces and en-suite bathrooms, and one of 40 m²), plus three children’s bedrooms – up to 14 guests.',
                    'common areas : 50 m² living room / kitchen / dining area and two additional separate lounges',
                    '5 bathrooms (including 2 separate), 6 toilets (2 separate), and 1 laundry room.',
                    'Air conditioning units, high-speed Wi-Fi, barbecues',
                    'sheets included, bathtowels included but beachtowels not included',
                    'pet allowed (only a single one) but not in bedrooms',
                    'The outdoor area for both relaxation and sports activities',
                    'heated saltwater secure,fenced, key-locked swimming pool (6 × 12 m)  sun loungers',
                    'basketball practice court (10 × 10 m), boules court, ping-pong table',
                    'Tennis in the nearby free municipal tennis court',
                    'A GR hiking trail in front of the house to follow to visit Saint-Véran (45 minutes one way) or Roquesaltes (2 hours one way).',
                    'The estate is located on the heights of the Dourbie Valley, within the Grands Causses, a UNESCO World Heritage Site. ',
                    '20 km from Millau and the A75 motorway.',
                    'for food, bakery  go to Millau',
                    'ideal place for  sports, nature, and culture: Templar and Hospitaller towns and bastides, spectacular caves and sinkholes, the rock formations of Montpellier-le-Vieux, the archaeological site of La Graufesenque, and of course the famous viaduct.',
                    'Each season has its own charm. In winter, cross-country skiing at Mont Aigoual (40 km away), dark starry nights, and truffle gastronomy; spring and autumn are perfect for long walks, sunny lunches, and evenings by the fireplace.',
                    'This estate offers space, serenity, and freedom for both children and adults, in a friendly and comfortable setting.'])

new_doc = Document(page_content=summary)
documents.insert(0, documents[0])
documents[0].page_content = summary
chunks = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50).split_documents(documents)

#Créer la base Chroma
db = Chroma.from_documents(
    documents=chunks,
    embedding=OpenAIEmbeddings(openai_api_key=secret_key)
)
# dossier static
app.mount("/static", StaticFiles(directory="static"), name="static")

templates = Jinja2Templates(directory='templates')

chat_responses = []


@app.get("/", response_class=HTMLResponse)
async def chat_page(request: Request):
    return templates.TemplateResponse("home.html", {"request":request, "chat_responses":chat_responses})

#initialisation
chat_log = [{'role': 'system',
             'content': 'you are a helpful assistant. Never repeat previous answers.Give short and precise answer'},
            {'role': 'assistant',
             'content': 'Here is the document the user wants you to use:Large Comfortable peaceful Residence in a Private Estate  of over 100 hectares with Pool.'
                        'Breathtaking Views over the Causses plateaux and the Dourbie Valley.'
                        '7 bedrooms – including 4 master suites (two of 30 m² with large terraces and en-suite bathrooms, and one of 40 m²), plus three children’s bedrooms – up to 14 guests.'
                        'common areas : 50 m² living room / kitchen / dining area and two additional separate lounges'
                        '5 bathrooms (including 2 separate), 6 toilets (2 separate), and 1 laundry room.'
                        'Air conditioning units, high-speed Wi-Fi, barbecues'
                        'sheets included, bathtowels included but beachtowels not included'
                        'pet allowed (only a single one) but not in bedrooms'
                        'The outdoor area for both relaxation and sports activities'
                        'heated saltwater secure,fenced, key-locked swimming pool (6 × 12 m)  sun loungers'
                        'basketball practice court (10 × 10 m), boules court, ping-pong table'
                        'Tennis in the nearby free municipal tennis court'
                        'A GR hiking trail in front of the house to follow to visit Saint-Véran (45 minutes one way) or Roquesaltes (2 hours one way).'
                        'The estate is located on the heights of the Dourbie Valley, within the Grands Causses, a UNESCO World Heritage Site. '
                        '20 km from Millau and the A75 motorway.'
                        'for food, bakery  go to Millau'
                        'ideal place for  sports, nature, and culture: Templar and Hospitaller towns and bastides, spectacular caves and sinkholes, the rock formations of Montpellier-le-Vieux, the archaeological site of La Graufesenque, and of course the famous viaduct.'
                        'Each season has its own charm. In winter, cross-country skiing at Mont Aigoual (40 km away), dark starry nights, and truffle gastronomy; spring and autumn are perfect for long walks, sunny lunches, and evenings by the fireplace.'
                        'This estate offers space, serenity, and freedom for both children and adults, in a friendly and comfortable setting.'}

]

#server connection

# server connection
@app.websocket("/ws")
async def chat(websocket: WebSocket):
    await websocket.accept()
    llm = ChatOpenAI(
        model="gpt-4o-mini",
        openai_api_key=secret_key,
        temperature=0.6,
        max_tokens=1000  # 👈 augmente ici
    )
    print("llm construit")
    while True:
        user_input = await websocket.receive_text()
        chat_log.append({'role': 'user', 'content': user_input})
        chat_responses.append(user_input)
        try:
            # avec le pdf
            docs = db.similarity_search(user_input, k=4)
            context = "\n\n".join([d.page_content for d in docs])
            # 🧠 Messages style OpenAI
            messages = [
                {
                    "role": "system",
                    "content": "you are a helpful assistant. Give short and precise answer. If you don't know, say it."
                },
                {
                    "role": "user",
                    "content": f"Contexte:\n{context}\n\nQuestion:\n{user_input}"
                }
            ]

            # ?? Appel LLM
            # response = llm.invoke(prompt)
            full_response = ''
            async for chunk in llm.astream(messages):
                token = chunk.content or ""
                full_response += token
                # ?? envoie chaque morceau au frontend
                await websocket.send_text(token)

            chat_responses.append(full_response)

        except Exception as e:
            await websocket.send_text(f"Error: {str(e)}")
            break


@app.post("/", response_class=HTMLResponse)
async def chat(request: Request, user_input: Annotated[str,Form()]):
    chat_log.append({'role' : 'user', 'content': user_input})

    chat_responses.append(user_input)

    response = openai.chat.completions.create(
        #model='gpt-3.5-turbo',
        model='gpt-4o-mini',
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

