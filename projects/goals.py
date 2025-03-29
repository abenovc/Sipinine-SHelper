import streamlit as st
import json
from datetime import datetime
 
DATA_FILE = "data_bases/tasks.json"
 
def load_goals():
    try:
        with open(DATA_FILE, "r") as file:
            return json.load(file)
    except (FileNotFoundError):
        return []
 
def save_goals(goals):
    with open(DATA_FILE, "w") as file:
        json.dump(goals, file, indent=4)
 
def get_current_time():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")
 
def sort_by_date(goal):
    return goal["created_at"]
 
def sort_by_status(goal):
    return goal["completed"]
 
goals = load_goals()
 
st.title("✨ My goals ✨")
 
new_goal = st.text_input("🔖 Add your new goal")
if st.button("➕ Add goal"):
    if new_goal:
        goals.append({
            "text": new_goal,
            "rating": 0,
            "created_at": get_current_time(),
            "subgoals": [],
            "completed": False,
            "show_subgoals": False,
        })
        save_goals(goals)
        st.rerun()
 
sort_option = st.selectbox("🔄 Sort of goals", ["By date 🗓️", "By status ⚖️"])
 
if sort_option == "By date 🗓️":
    goals.sort(key=sort_by_date, reverse=True)
elif sort_option == "By status ⚖️":
    goals.sort(key=sort_by_status, reverse=True)
 
completed_goals = sum(1 for goal in goals if goal["completed"])
total_goals = len(goals)
st.write(f"✅ Completed goals: {completed_goals} из {total_goals}")
 
st.subheader("📝 My goals:")
 
def get_goal_color(subgoals, goal):
    if goal["completed"]:
        return "background-color: #32CD32;"
    else:
        completed_subgoals = sum(1 for subgoal in subgoals if subgoal["completed"])
        if len(subgoals) == 0:
            return "background-color: #FF6347;"
        elif completed_subgoals * 100 / len(subgoals) >= 40:
            return "background-color: #FFD700;"
        else:
            return "background-color: #FF6347;"
 
for i, goal in enumerate(goals):
    col1, col2, col3 = st.columns([0.6, 0.2, 0.2])
 
    goal_color = get_goal_color(goal["subgoals"], goal)
    goal_text = f"{goal['text']} (Created: {goal['created_at']})"
 
    col1.markdown(f'<div style="{goal_color} padding: 10px; border-radius: 5px; margin-bottom: 10px;">{goal_text}</div>', unsafe_allow_html=True)
 
    if 'edit_task' in st.session_state and st.session_state.edit_task == goal['text']:
        new_goal_text = st.text_input("✏️ Edit your goal", value=st.session_state.edit_task_text, key=f"edit_input_{goal['created_at']}")
        if st.button("💾 Save changes", key=f"save_{goal['created_at']}"):
            goal['text'] = new_goal_text
            save_goals(goals)
            del st.session_state.edit_task
            del st.session_state.edit_task_text
            st.rerun()
    else:
        if col1.button("✏️ Edit goal", key=f"edit_{goal['created_at']}"):
            st.session_state.edit_task = goal['text']
            st.session_state.edit_task_text = goal['text']
            st.rerun()
 
    if col2.button(f"✅ Complete goal", key=f"complete_{goal['created_at']}"):
        goal['completed'] = not goal['completed']
        save_goals(goals)
        st.rerun()
 
    new_subgoal_text = st.text_input(f"Add subgoal", key=f"subgoal_input_{goal['created_at']}")
    if col1.button(f"➕ Add subgoal", key=f"add_subgoal_{goal['created_at']}"):
        if new_subgoal_text:
            goal["subgoals"].append({
                "text": new_subgoal_text,
                "completed": False,
            })
            save_goals(goals)
            st.rerun()
 
    if col3.button(f"🔽 Show subgoals" if not goal['show_subgoals'] else f"🔼 Hide subgoals", key=f"toggle_subgoals_{goal['created_at']}"):
        goal['show_subgoals'] = not goal['show_subgoals']
        save_goals(goals)
        st.rerun()
 
    if goal['show_subgoals']:
        for j, subgoal in enumerate(goal["subgoals"]):
            col1, col2, col3 = st.columns([0.6, 0.2, 0.2])
 
            subgoal_text = f"{subgoal['text']} (Completed: {'Yes' if subgoal['completed'] else 'No'})"
            col1.markdown(f'<div>{subgoal_text}</div>', unsafe_allow_html=True)
 
            if 'edit_subgoal' in st.session_state and st.session_state.edit_subgoal == subgoal['text']:
                new_subgoal_text = st.text_input(f"✏️ Edit your subgoal", value=st.session_state.edit_subgoal_text, key=f"subgoal_input_edit_{goal['created_at']}_{subgoal['text']}")
                if st.button("💾 Save changes", key=f"save_subgoal_{goal['created_at']}_{subgoal['text']}"):
                    subgoal['text'] = new_subgoal_text
                    save_goals(goals)
                    del st.session_state.edit_subgoal
                    del st.session_state.edit_subgoal_text
                    st.rerun()
            else:
                if col2.button(f"✏️ Edit subgoal", key=f"edit_subgoal_{goal['created_at']}_{subgoal['text']}"):
                    st.session_state.edit_subgoal = subgoal['text']
                    st.session_state.edit_subgoal_text = subgoal['text']
                    st.rerun()
 
            completed = col1.checkbox(f"✅ {subgoal['text']}", value=subgoal["completed"], key=f"subgoal_checkbox_{goal['created_at']}_{subgoal['text']}")
 
            if completed != subgoal["completed"]:
                subgoal["completed"] = completed
                save_goals(goals)
                st.rerun()
 
            if col3.button(f"🗑️ Delete subgoal", key=f"del_subgoal_{goal['created_at']}_{subgoal['text']}"):
                goal["subgoals"].pop(j)
                save_goals(goals)
                st.rerun()
 
    if col3.button(f"🗑️ Delete goal", key=f"del_{goal['created_at']}"):
        goals.pop(i)
        save_goals(goals)
        st.rerun()
