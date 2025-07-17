import os
import dotenv
from agents import Agent,Runner,function_tool,set_tracing_disabled
from agents.extensions.models.litellm_model import LitellmModel
import asyncio
from bs4 import BeautifulSoup
import requests
import chainlit as cl

set_tracing_disabled(disabled=True)
dotenv.load_dotenv()
os.environ['GEMINI_API_KEY']=os.getenv('GEMINI_API_KEY')
model='gemini/gemini-2.0-flash'

@function_tool
def get_user_data(min_age:int)->list[dict]:
    'Retrieve user data based on minimum age'
    users = [
        {"name": "Muneeb", "age": 22},
        {"name": "Muhammad Ubaid Hussain", "age": 25},
        {"name": "Azan", "age": 19},

    ]
    return [user for user in users if user['age'] >= min_age]
    


@function_tool
def send_whatsapp(contact: str, message: str) -> str:
    instance_id = "instance133066"
    token = "uldzah8l1xnwzz9q"
    url = f"https://api.ultramsg.com/{instance_id}/messages/chat"
    payload = {
        "token": token,
        "to": contact,
        "body": message
    }
    response = requests.post(url, data=payload)
    
    if response.status_code == 200:
        print('✅ Message sent via UlrtaMSG!')
        return "✅ Message sent via UlrtaMSG!"
    else:
        return f"❌ Failed: {response.text}"
    
    

@function_tool
def browser_search(query: str) -> str:
    """
    Search the web using DuckDuckGo and return the top 3 result snippets.
    """
    url = f"https://html.duckduckgo.com/html?q={query}"
    headers = {
        "User-Agent": "Mozilla/5.0"
    }
    res = requests.get(url, headers=headers)
    soup = BeautifulSoup(res.text, "html.parser")
    results = soup.select('.result__snippet')

    if not results:
        return "No results found."

    return '\n\n'.join([r.get_text(strip=True) for r in results[:3]])

Match_finder=Agent(
    name='Auntie',
    model=LitellmModel(model=model),
    instructions="You are a warm and wise 'Rishtey Wali Auntie' who helps people find matches,Use the get_user_data tool to find users of minimum age 20 then use browser_search tools to fetch their details from linkedIn. Then format their details (name and age and profession) into a message and send it to +923311347822 using the send_whatsapp tool.",
    tools=[get_user_data,browser_search,send_whatsapp]
    
)

@cl.on_chat_start
async def handling_history():
    cl.user_session.set('history',[])
    await cl.Message("Beta ji, Rishta Wali Auntie at your service! 💍 Now tell me, what age range are we looking for? And any other shartien or khaas requirements? Don’t be shy, aunty won’t judge!").send()
    
    
@cl.on_message
async def main(message:cl.Message):
    history=cl.user_session.get('history')
    history.append({'role':"user","content":message.content})
    
    result = Runner.run_sync(
    starting_agent=Match_finder,
    input = history

)
    history.append({"role":"assistant","content":result.final_output})
    cl.user_session.set('history',history)
    
    await cl.Message(
        content=result.final_output
    ).send()
    
    
    # okay so my name is Alishba wajahat and i want a well settled rishta of min age 25



