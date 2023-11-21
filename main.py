from fastapi import FastAPI, Request, Form
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from pymongo import MongoClient
import uvicorn

app = FastAPI()

template = Jinja2Templates(directory='templates')
app.mount("/static", StaticFiles(directory="static"), name="static")

mongo_client = MongoClient("mongodb://localhost:27017")
my_db = mongo_client['testdb']
my_col = my_db['collection']

class Animal(BaseModel):
    name: str
    age: int
    description: str
    image: str

@app.get('/login')
async def login(request: Request):
    return template.TemplateResponse('login.html', {'request':request})

@app.get('/')
async def index(request:Request):
    animals = list(my_col.find({}))
    return template.TemplateResponse('index.html', {'request':request, 'animals':animals})

@app.route('/new')
async def create_new(request: Request):
    if request.method == 'POST':
        # Handle form submission
        form = await request.form()
        name = form.get('name')
        age = form.get('age')
        description = form.get('description')
        image = form.get('image')

        new_animal = Animal(name=name, age=int(age), description=description, image=image)
        my_col.insert_one(new_animal.dict())
        return template.TemplateResponse('new.html', {'request': request})

    return template.TemplateResponse('new.html', {'request': request})

@app.get('/animal/{name}')
def get_animal(request: Request, name:str):
    animal = my_col.find_one({"name": name})
    return template.TemplateResponse('animal.html', {"request":request, "animal": animal})

@app.post('/submit')
async def submit(nm:str = Form(...), pwd: str = Form(...)):
    return HTMLResponse(f"<h1>Hello {nm}</h1>")

if __name__ == '__main__':
    uvicorn.run(app, host='127.0.0.1', port=8000)