import streamlit as st
import json
from datetime import date
import os
 
def load_json():
    if not os.path.exists('data_bases/plan.json'):
        with open('data_bases/plan.json', 'w') as f:
            json.dump({}, f)
    with open('data_bases/plan.json', 'r') as f:
         return json.load(f)
 
def save_json(plan):
    with open('data_bases/plan.json', 'w') as f:
        json.dump(plan, f, indent=4)
 
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
 
# Выбор дня
col4, col5, col6 = st.columns([2, 2, 1])
 
col1, col2, col3 , col4 = st.columns([1.2, 1.3 , 1.1,9])
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
# st.subheader("🔍 **Поиск задач**")
# st.session_state.search_query = st.text_input("Введите название задачи", value=st.session_state.search_query, placeholder="Например, решить алгебру")
st.divider()
 
if selected_day in plan and plan[selected_day]:
    st.subheader(f"🗂 **Tasks on {selected_day}**")
    plans = {}
    for time in sorted(plan[selected_day]):
        plans[time] = plan[selected_day][time]
 
    for time, task_info in plans.items():
        task = task_info["task"]
        description = task_info["description"]
 
        if st.session_state.search_query.lower() in task.lower():
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
else:
    st.info(f"✨ You don't have any tasks for {selected_day}. Add the first one!")
 
st.divider()
 
if st.session_state.toast_message:
    for message in st.session_state.toast_message:
        st.toast(message)
    st.session_state.toast_message = []