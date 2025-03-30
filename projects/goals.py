import streamlit as st
import json
from datetime import datetime

DATA_FILE = "data_bases/task.json"

def load_goals():
    try:
        with open(DATA_FILE, "r") as file:
            return json.load(file)
    except FileNotFoundError:
        return []

def save_goals(goals):
    with open(DATA_FILE, "w") as file:
        json.dump(goals, file, indent=4)

def get_current_time():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def sort_by_date(goal):
    return goal["created_at"]

def sort_by_status(goal):
    return goal["goal_completed"]

goals = load_goals()

st.title("✨ My goals ✨")

new_goal = st.text_input("🔖 Add your new goal")
if st.button("➕ Add goal"):
    if new_goal:
        goals.append({
            "goal_name": new_goal,
            "created_at": get_current_time(),
            "subgoals": [{
                "subgoal_name": "completed",
                "subgoal_completed": False,
            }],
            "goal_completed": False,
            "show_subgoals": False,
        })
        save_goals(goals)
        st.rerun()

sort_option = st.selectbox("🔄 Sort of goals", ["By date 🗓️", "By status ⚖️"])

if sort_option == "By date 🗓️":
    goals.sort(key=sort_by_date, reverse=True)
elif sort_option == "By status ⚖️":
    goals.sort(key=sort_by_status, reverse=True)

completed_goals = sum(1 for goal in goals if goal["goal_completed"])
total_goals = len(goals)
st.write(f"✅ Completed goals: {completed_goals} из {total_goals}")

st.subheader("📝 My goals:")

def get_goal_color(subgoals, goal):
    completed_subgoals = sum(1 for subgoal in subgoals if subgoal["subgoal_completed"])
    if goal["goal_completed"]:
        return "background-color: #32CD32;"
    elif completed_subgoals * 100 / len(subgoals) >= 40 and completed_subgoals != len(subgoals):
        return "background-color: #FFD700;"
    elif completed_subgoals == len(subgoals):
        return "background-color: #32CD32;"
    else:
        return "background-color: #FF6347;"

for i, goal in enumerate(goals):
    if goal["goal_name"] != "Sample":
        col1, col2, col3 = st.columns([0.6, 0.2, 0.2])

        goal_color = get_goal_color(goal["subgoals"], goal)
        goal_text = f"{goal["goal_name"]} (Created: {goal['created_at']})"

        col1.markdown(f'<div style="{goal_color} padding: 10px; border-radius: 5px; margin-bottom: 10px;">{goal_text}</div>', unsafe_allow_html=True)

        with col1.expander(f"✏️ Edit goal"):
            new_goal_text = st.text_input("✏️ Edit your goal", value=goal["goal_name"], key=f"edit_input_{goal['created_at']}")
            if st.button("💾 Save changes", key=f"save_{goal['created_at']}"):
                goal['goal_name'] = new_goal_text
                save_goals(goals)
                st.rerun()

        if col3.button(f"🔽 Show subgoals" if not goal['show_subgoals'] else f"🔼 Hide subgoals", key=f"toggle_subgoals_{goal['created_at']}"):
            goal['show_subgoals'] = not goal['show_subgoals']
            save_goals(goals)
            st.rerun()

        if goal['show_subgoals']:
            with col1.expander(f"➕ Add subgoal"):
                new_subgoal_text = st.text_input(f"Add a new subgoal", key=f"subgoal_input_{goal['created_at']}")
                if st.button("➕ Add subgoal", key=f"add_subgoal_{goal['created_at']}"):
                    if new_subgoal_text:
                        if not any(subgoal['subgoal_name'] == new_subgoal_text for subgoal in goal["subgoals"]):
                            goal["subgoals"].append({"subgoal_name": new_subgoal_text, "subgoal_completed": False})
                            save_goals(goals)
                            st.rerun()
                        else:
                            st.warning("Subgoal already exists.")

            for j, subgoal in enumerate(goal["subgoals"]):
                if subgoal["subgoal_name"] == "completed":
                    completed = st.checkbox(f"✅ {subgoal['subgoal_name']}", value=subgoal["subgoal_completed"], key=f"subgoal_checkbox_{goal['created_at']}_{subgoal['subgoal_name']}")
                    col1, col2, col3 = st.columns([0.4, 0.4, 0.2])
                    goal["goal_completed"] = completed
                else:
                    col1, col2, col3 = st.columns([0.4, 0.4, 0.2])
                    completed = col1.checkbox(f"✅ {subgoal['subgoal_name']}", value=subgoal["subgoal_completed"], key=f"subgoal_checkbox_{goal['created_at']}_{subgoal['subgoal_name']}")
                
                if completed != subgoal["subgoal_completed"]:
                    subgoal["subgoal_completed"] = completed
                    save_goals(goals)
                    st.rerun()

                if subgoal["subgoal_name"] != "completed":
                    with col2.expander(f"✏️ Edit subgoal"):
                        new_subgoal_text = st.text_input(f"Edit your subgoal", value=subgoal["subgoal_name"], key=f"edit_subgoal_input_{goal['created_at']}_{subgoal['subgoal_name']}")
                        if st.button(f"💾 Save changes", key=f"save_subgoal_{goal['created_at']}_{subgoal['subgoal_name']}"):
                            subgoal["subgoal_name"] = new_subgoal_text
                            save_goals(goals)
                            st.rerun()

                    if col3.button(f"🗑️ Delete subgoal", key=f"del_subgoal_{goal['created_at']}_{subgoal['subgoal_name']}"):
                        goal["subgoals"].pop(j)
                        save_goals(goals)
                        st.rerun()

        with col3:
            if st.button(f"🗑️ Delete goal", key=f"del_{goal['created_at']}"):
                goals.pop(i)
                save_goals(goals)
                st.rerun()
