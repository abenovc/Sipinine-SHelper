import streamlit as st
import requests
import pandas as pd
import numpy as np
import json
import os
from datetime import date
from fastapi import FastAPI

#app = FastAPI()
#
## Твой Google API-ключ и Search Engine ID
#API_KEY = "HIDDEN"
#CX = "34ed371aeced4441a"
#GOOGLE_API_Y = "http://127.0.0.1:8000/search?query="
#
#def google_search(query):
#    """Делает запрос в Google Custom Search API и возвращает результаты."""
#    url = f"https://www.googleapis.com/customsearch/v1?q={query}&key={API_KEY}&cx={CX}"
#    response = requests.get(url)
#    results = response.json()
#
#    if "items" in results:
#        return [{"title": item["title"], "link": item["link"]} for item in results["items"]]
#    return []
#
#@app.get("/search")
#def search(query: str):
#    """Эндпоинт для поиска в Google."""
#    return google_search(query)

api_key = "HIDDEN"
url = "https://api.openai.com/v1/chat/completions"
 
headers = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {api_key}"
}
data_GPT = {
    "model": "gpt-4o-mini",
    "messages": [
        {"role": "system", "content": "You are a helpful assistant"},
        {"role": "system", "content": "Ты — помощник по редактированию JSON. В JSON файлах могут храниться события дней с их назвением, описанием, временем, датой или же цели на определенные дни с их назвением, подцелями, временем, датой, еще несколькими значениями. Ты умеешь одновременно изменять все JSON файлы. Можешь заполнять данные информацией которая кажется тебе правильной"},
        {"role": "system", "content": "Тебе нельзя генерировать изображения и видео."}
    ],
    "max_tokens": 6000,
    "temperature": 0.7,
    "top_p": 1.0,
    "frequency_penalty": 0.0,
    "presence_penalty": 0.0
}

def load_json():
    if not os.path.exists('data_bases/plan.json'):
        with open('data_bases/plan.json', 'w') as f:
            json.dump({}, f)
    with open('data_bases/plan.json', 'r') as f:
         return json.load(f)

def save_json(plan):
    with open('data_bases/plan.json', 'w') as f:
        json.dump(plan, f, indent=4)

def load_task():
    if not os.path.exists('data_bases/task.json'):
        with open('data_bases/task.json', 'w') as f:
            json.dump({}, f)
    with open('data_bases/task.json', 'r') as f:
         return json.load(f)

def save_task(task):
    with open('data_bases/task.json', 'w') as f:
        json.dump(task, f, indent=4)

def process_request(user_request, json_data):
    prompt = f"""
    Ты — помощник, который изменяет JSON-файл на основе запроса пользователя.Тебе нельзя генерировать изображения и видео.
    В JSON файле храняться события дней с их назвением, описанием, временем, датой. Можешь заполнять данные информацией которая кажется тебе правильной
    Текущий JSON:
    {json.dumps(json_data, indent=4, ensure_ascii=False)}
 
    Запрос: "Добавь следующие ЗАДАЧИ в РАСПИСАНИЕ {user_request}"
 
    Верни ОТЛИЧАЮЩИЙСЯ JSON, БЕЗ пояснений. Если какая-то информация про дату, время или задание не указано, придумай сам, но не пиши свободное время или похожее. Ты можешь заменять сущетсвующие даты если пользователь не против
    """
 
#    data_GPT["messages"][2] = {"role": "user", "content": prompt}
    data_GPT["messages"].append({"role": "user", "content": prompt})
 
    res = requests.post(url, headers=headers, data=json.dumps(data_GPT))
    response = res.json()
 
    try:
        new_json = json.loads(response["choices"][0]["message"]["content"])
        return new_json
    except json.JSONDecodeError:
        return json_data

def process_task(user_request, json_data):
    prompt = f"""
    Ты — помощник, который изменяет JSON-файл на основе запроса пользователя.
    В JSON файле храняться цели на определенные дни с их назвением, подцелями, временем, датой и еще несколькими значениями. Можешь заполнять данные информацией которая кажется тебе правильной
    Текущий JSON:
    {json.dumps(json_data, indent=4, ensure_ascii=False)}
    
    Запрос: "Добавь следующую ЦЕЛЬ -> {user_request}"
 
    Верни ОТЛИЧАЮЩИЙСЯ JSON, БЕЗ пояснений. Если какая-то информация не указана то придумай сам
    """
 
    data_GPT["messages"].append({"role": "user", "content": prompt})
 
    res = requests.post(url, headers=headers, data=json.dumps(data_GPT))
    response = res.json()
 
    try:
        new_json = json.loads(response["choices"][0]["message"]["content"])
        return new_json
    except json.JSONDecodeError:
        return json_data

def upd(day, time, task, description):
    if day not in plan:
        plan[day] = {}
    plan[day][time] = {"task": task, "description": description}
    save_json(plan)

def delete(day, time):
    del plan[day][time]
    if not plan[day]:
        del plan[day]
    save_json(plan)

st.set_page_config(page_title="🕒 Time Management", layout="wide")

if "toast_message" not in st.session_state:
    st.session_state.toast_message = []
if "selected_day" not in st.session_state:
    st.session_state.selected_day = date.today()
if "search_query" not in st.session_state:
    st.session_state.search_query = ""

st.header("🕒 Time-Management")
st.subheader(" Plan your tasks by day and don't miss important things! 🚀")
st.divider()

plan = load_json()
task_main = load_task()

if "plan" not in st.session_state:
    st.session_state.plan = plan

col4, col5, col6 = st.columns([2, 2, 1])

col1, col2, col3 , col4 , col5 = st.columns([1.4, 1.4 , 1.3, 1.45 , 8])
with col1:
    with st.popover("📅 ***Select day***"):
        st.subheader("Selected date")
        st.session_state.selected_day = st.date_input("", st.session_state.selected_day, format="DD.MM.YYYY")
        
selected_day = st.session_state.selected_day.strftime("%Y-%m-%d")
with col2:
    with st.popover("➕ **Add a task**"):
        st.subheader("📝 New Task")
        task = st.text_input("Enter the task", placeholder="For example, solve algebra")
        description = st.text_area("Enter a description", placeholder="Task Details", max_chars=50)
        time = st.time_input("Choose a time")
        formatted = ""
        if time:
            formatted = time.strftime("%H:%M")
        
        if st.button("✅ Add", use_container_width=True):
            if task and formatted:
                upd(selected_day, formatted, task, description)
                st.session_state.toast_message.append(f"✅ Task **'{task}'** on **{formatted}** added to {selected_day}!")
                st.rerun()
            else:
                st.toast("⚠️ Please fill in all fields..")
with col3:
    @st.dialog("🔍 Task Search")
    def search():
        st.session_state.search_query = st.text_input("Enter the task name", value=st.session_state.search_query, placeholder="For example, solve algebra")
    if st.button("🔍 **Task Search**"):
        search()
with col4:
    @st.dialog("🤖 AI Function")
    def ai_func():
        global plan
        global task_main
        user_input = st.text_area("Enter your goal or plan", placeholder = "For example, prepare for IELTS")
        if st.button("Применить"):
            if user_input:
                updated_json = process_request(user_input, plan)
                save_json(updated_json)
                st.success("Schedule updated!")
                plan = updated_json
                updated_task = process_task(user_input , task_main)
                save_task(updated_task)
                st.success("Goal was added!")
                task_main = updated_task
                st.rerun()
            else:
                st.toast("⚠️ Please fill in all fields..")
    if st.button("🤖🧠 **AI Function**"):
        ai_func()

st.divider()



if selected_day in plan and plan[selected_day] and (len(plan[selected_day]) > 1 or (len(plan[selected_day]) == 1 and selected_day != "2025-03-30")):
    st.subheader(f"🗂 **Tasks on {selected_day}**")
    plans = {}
    for time in sorted(plan[selected_day]):
           plans[time] = plan[selected_day][time]
    
    for time, task_info in plans.items():
        task = task_info["task"]
        description = task_info["description"]
        
        if st.session_state.search_query.lower() in task.lower() and task != "Sample":
            with st.expander(f"⏰ **{time}** | ***{task}***"):
                st.write(f"📌**Description**: {description}")
                task1 = st.text_input("✏️ Update task", value=task, key=f"upd1{selected_day}{time}")
                description1 = st.text_area("✏️ Update description", value=description, key=f"desc1{selected_day}{time}", max_chars=50)
                col1, col2, col3 = st.columns([1, 2, 1])
                with col2:
                    if st.button("🔄 Update", key=f"upd{selected_day}{time}", use_container_width=True):
                        if task1:
                            upd(selected_day, time, task1, description1)
                            st.session_state.toast_message.append(f"✏️ The task : **{task1}** on **{time}** ({selected_day}) has been updated")
                            st.rerun()
                with col1:
                    if st.button("🗑️ Delete", key=f"del{selected_day}{time}", use_container_width=True):
                        delete(selected_day, time)
                        st.session_state.toast_message.append(f"🗑️ Task **{task}** on **{time}** is deleted from {selected_day}!")
                        st.rerun()
else :
    st.info(f"✨ You don't have any tasks for {selected_day}. Add the first one!")

st.divider()

if st.session_state.toast_message:
    for message in st.session_state.toast_message:
        st.toast(message)
    st.session_state.toast_message = []

