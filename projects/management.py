import streamlit as st
import requests
import pandas as pd
import numpy as np
import json
import os
from datetime import date
#a =b
#b = a
api_key = (HIDDEN API KEY)
url = "https://api.openai.com/v1/chat/completions"
 
headers = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {api_key}"
}
data_GPT = {
    "model": "gpt-4o-mini",
    "messages": [
        {"role": "system", "content": "You are a helpful assistant"},
        {"role": "system", "content": "Ты — помощник по редактированию JSON."},
        {"role": "user", "content": "user's prompt"}
    ],
    "max_tokens": 6000,
    "temperature": 0.7,
    "top_p": 1.0,
    "frequency_penalty": 0.0,
    "presence_penalty": 0.0
}

def load_json():
    if not os.path.exists('plan.json'):
        with open('plan.json', 'w') as f:
            json.dump({}, f)
    with open('plan.json', 'r') as f:
         return json.load(f)

def save_json(plan):
    with open('plan.json', 'w') as f:
        json.dump(plan, f, indent=4)

def process_request(user_request, json_data):
    prompt = f"""
    Ты — помощник, который изменяет JSON-файл на основе запроса пользователя.
    Текущий JSON:
    {json.dumps(json_data, indent=4, ensure_ascii=False)}
 
    Запрос: "{user_request}"
 
    Верни ОТЛИЧАЮЩИЙСЯ JSON, БЕЗ пояснений. Если какаято информация про дату,время или задание не указано придумай сам но не пиши свободное время или похожее
    """
 
    data_GPT["messages"][2] = {"role": "user", "content": prompt}
 
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

col4, col5, col6 = st.columns([2, 2, 1])

col1, col2, col3 , col4 = st.columns([1.3, 1.3 , 1.2,9])
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
user_input = st.text_area("Введите запрос", placeholder = "Например подготовка к IELTS")
 
if st.button("Применить"):
    if user_input:
        updated_json = process_request(user_input, plan)
        save_json(updated_json)
        st.success("Расписание обновлено!")
        plan = updated_json
        st.rerun()
    else:
        st.warning("Введите запрос!")

if st.session_state.toast_message:
    for message in st.session_state.toast_message:
        st.toast(message)
    st.session_state.toast_message = []

