import requests
import json
import os

from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from dotenv import load_dotenv


load_dotenv("./secret.env")

app = FastAPI()
templates = Jinja2Templates(directory="templates")
# shared context
data_storage = {'more_about_steps': {}}

# Mount the static files directory
app.mount("/static", StaticFiles(directory="static"), name="static")

headers = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {os.environ.get('API_KEY')}",
}


@app.get("/")
def home(request: Request):
    return templates.TemplateResponse(
        "index.html", {"request": request}
    )


class Item(BaseModel):
    description: str


class additionalInfo(BaseModel):
    step: str


@app.post("/generate-task-steps")
async def generate_task_steps(item: Item):
    data = {
        "model": "gpt-3.5-turbo",
        "messages": generate_message_second_approach(item.description),
    }

    data_storage["task_description"] = item.description

    # Consider user may ask to plan your return step in more detail

    response = requests.post(
        "https://api.openai.com/v1/chat/completions",
        headers=headers,
        data=json.dumps(data),
    )

    response_json = response.json()
    print(f"RESPONSE JSOON:  {response_json}")

    assistant_message = response_json["choices"][0]["message"]["content"]
    data_storage["assistant_answer"] = assistant_message
    print(f"assistant_message:  {assistant_message} ")

    tasks = parse_assistant_message(assistant_message)

    return {"tasks": tasks}


@app.post("/more-info-of-step")
async def more_info_of_step(item: additionalInfo):
    if item.step in data_storage['more_about_steps']:
        return {"moreInfo": data_storage['more_about_steps'][item.step]}

    if (
        data_storage["task_description"] is not None
        and data_storage["assistant_answer"] is not None
    ):
        data = {
            "model": "gpt-3.5-turbo",
            "messages": generate_message_with_more_info_of_step(
                item.step, data_storage['task_description']
            ),
        }

        # Consider user may ask to plan your return step in more detail

        response = requests.post(
            "https://api.openai.com/v1/chat/completions",
            headers=headers,
            data=json.dumps(data),
        )

        response_json = response.json()
        print(f"RESPONSE JSOON:  {response_json}")

        assistant_message = response_json["choices"][0]["message"]["content"]

        print(f"assistant_message:  {assistant_message} ")
        data_storage['more_about_steps'][item.step] = assistant_message

        return {"moreInfo": assistant_message}

    return {"moreInfo": "problem with API"}


def generate_message_with_more_info_of_step(step: str, task_description: str):
    start_message = generate_message_second_approach(task_description=task_description)
    start_message.extend(
        [
            {"role": "assistant", "content": data_storage['assistant_answer']},
            {
                "role": "user",
                "content": f"provide more information about this step: {step}",
            },
        ]
    )
    return start_message


def generate_message_first_approach(task_description: str):
    return [{
            "role": "system",
            "content": "You are a helpful assistant and help user to plan task into steps: what to do first, second and so on. Please return next format: 1. first step\n2. second step\n3. third step and so on. Nothing more, just numbering.",
        },{
            "role": "user",
            "content": f"Plan a task, the description of which is as follows: {task_description}. Return the answer in the same form as in the previous answer",
        }]

def generate_message_second_approach(task_description: str):
    return [
        {
            "role": "system",
            "content": "You are a helpful assistant and help user to plan task into steps: what to do first, second and so on.",
        },
        {
            "role": "user",
            "content": "Plan a task, the description of which is as follows: How to learn the Angular framework.",
        },
        {
            "role": "assistant",
            "content": "1. Understand the basics of Angular.\n2. Learn TypeScript.\n3. Set up your development environment.",
        },
        {
            "role": "user",
            "content": "Plan a task, the description of which is as follows: I need to do customer analysis.",
        },
        {
            "role": "assistant",
            "content": "1. Define the purpose and scope of customer analysis.\n2. Collect customer data through surveys, interviews, and online analytics.\n3. Analyze the data to identify patterns and trends in customer behavior.\n4. Segment customers based on their shared characteristics and needs.\n5. Develop customer personas that represent different customer types.\n6. Use insights from customer analysis to inform marketing, product development, and sales strategies.",
        },
        {
            "role": "user",
            "content": "Plan a task, the description of which is as follows: How to learn the Django framework.",
        },
        {
            "role": "assistant",
            "content": "1. Understand the basics of Django and web development.\n2. Learn Python.\n3. Set up your development environment.\n4. Build a simple application\n5.Learn advanced topics",
        },
        {
            "role": "user",
            "content": f"Plan a task, the description of which is as follows: {task_description}. Return the answer in the same form as in the previous answer",
        },
    ]


def parse_assistant_message(msg: str):
    steps = msg.split("\n")
    for i in range(len(steps)):
        str_to_clean = steps[i]
        steps[i] = str_to_clean[3 : len(str_to_clean) - 1]
    return steps


# tasks_mock = ['Understand the rules of basketball and the basic skills involved', 'Find a local basketball court or team to practice with']

# @app.post("/generate-task-steps")
# async def generate_task_steps_mock(item: Item):
#     return {'tasks': tasks_mock}
