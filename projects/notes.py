import streamlit as st
import sqlite3
from datetime import datetime

def init():
	connection = sqlite3.connect("data_bases/notes.db")
	operation = connection.cursor()
	operation.execute("""
		CREATE TABLE IF NOT EXISTS notes (
			id integer primary key autoincrement,
			title text not null,
			content text not null,
			timer text not null,
			tags text 
		)
	""")
	connection.commit()
	connection.close()

def add_note(note_title, note_content, note_tags):
    connection = sqlite3.connect("data_bases/notes.db")
    operation = connection.cursor()
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    tags_str = ", ".join(note_tags)

    operation.execute("INSERT INTO notes (title, content, timer, tags) values (?, ?, ?, ?)", (note_title, note_content, current_time, tags_str))

    connection.commit()
    connection.close()

def get_note():
	connection = sqlite3.connect("data_bases/notes.db")
	operation = connection.cursor()

	operation.execute("SELECT id, title, content, timer, tags FROM notes ORDER BY timer DESC")
	list_notes = operation.fetchall()
	connection.close()
	return list_notes

def filter_get_note(selected_tags):
    connection = sqlite3.connect("data_bases/notes.db")
    operation = connection.cursor()

    query = "SELECT id, title, content, timer, tags FROM notes WHERE " + " OR ".join(["tags LIKE ?" for hz in selected_tags])
    options = [f"%{x}%" for x in selected_tags]

    operation.execute(query, options)
    list_notes = operation.fetchall()
    connection.close()
    return list_notes

def delete_note(note_id):
	connection = sqlite3.connect("data_bases/notes.db")
	operation = connection.cursor()

	operation.execute("DELETE FROM notes WHERE id = ?", (note_id,))
	connection.commit()
	connection.close()

def update_note(note_id, new_content, note_tags):
    connection = sqlite3.connect("data_bases/notes.db")
    operation = connection.cursor()
    tags_str = ", ".join(note_tags)

    operation.execute("UPDATE notes SET content = ?, tags = ? WHERE id = ?", (new_content, tags_str, note_id))
    connection.commit()
    connection.close()

def init_all_tags():
    connection = sqlite3.connect("data_bases/tags.db")
    operation = connection.cursor()
    operation.execute("""
        CREATE TABLE IF NOT EXISTS all_tags (
            list_tags text
        )
    """)
    operation.execute("SELECT count(*) FROM all_tags")
    if operation.fetchone()[0] == 0:
        operation.execute("INSERT INTO all_tags (list_tags) VALUES ('')")

    connection.commit()
    connection.close()

def update_init_tags(all_tags_promt):
    connection = sqlite3.connect("data_bases/tags.db")
    operation = connection.cursor()
    all_tags_str = ", ".join(all_tags_promt)

    operation.execute("UPDATE all_tags SET list_tags = ?", (all_tags_str,))
    connection.commit()
    connection.close()

def get_init_tags():
    connection = sqlite3.connect("data_bases/tags.db")
    operation = connection.cursor()

    operation.execute("SELECT list_tags FROM all_tags")
    result = operation.fetchone()
    connection.close()

    if result and result[0]:
        return result[0].split(", ")
    return []


init()
init_all_tags()

if "init_tags" not in st.session_state:
    st.session_state.init_tags = []

sz = get_init_tags()

if len(sz) > 0:
    st.session_state.init_tags = sz

st.header("📒 Notion")

colS1, colS2 = st.columns([0.1, 0.1])

if "selected_tags" not in st.session_state:
    st.session_state.selected_tags = []

with colS1:
    st.session_state.selected_tags = st.multiselect("Searching By Tags", st.session_state.init_tags)

col1_plus, col3_plus, col2_plus = st.columns([0.6, 0.11, 0.2])

with col1_plus:
    if st.button(":heavy_plus_sign:"):
        @st.dialog("New Note")
        def select():
            new_title = st.text_input("Add New Title")
            new_note = st.text_area("Add New Note")
            key_val = 1
            current_list = get_note()
            if len(current_list):
                key_val = current_list[-1][0] + 1
            new_tags = st.multiselect(
                "Choose Tags for your New Note",
                st.session_state.init_tags,
                key = f"selectM_{key_val}"
            )
            if st.button("Add"):
                if new_note.strip() and new_title.strip():
                    add_note(new_title, new_note, new_tags)
                    st.rerun()
        select()

with col2_plus:
    if st.button("All Tags"):
        @st.dialog("All Tags")
        def select_all_tags():
            new_all_tags = st.text_input("Select Your Own Tags", value = ", ".join(st.session_state.init_tags))
            new_all_tags = new_all_tags.replace(" ", "")
            st.session_state.init_tags = new_all_tags.split(",")
            update_init_tags(st.session_state.init_tags)
            if st.button("Update"):
                st.rerun()
        select_all_tags()

st.subheader("📌 My Notes:")

list_notes = get_note()

with col3_plus:
    if st.button("Search") and st.session_state.selected_tags:
        list_notes = filter_get_note(st.session_state.selected_tags)
    else:
        list_notes = get_note()

grouped_notes = {}
for note in list_notes:
    note_date = note[3].split(" ")[0]
    if note_date not in grouped_notes:
        grouped_notes[note_date] = []
    grouped_notes[note_date].append(note)

if grouped_notes == {}:
	st.info(f"✨ You don't have any Notes. Add the first one!")
else:
    for date, grouped_list_notes in grouped_notes.items():
        st.markdown(f"### 📅 {date}")
        for note in grouped_list_notes:
            with st.expander(f"# 📝 **{note[1]}**"):
                new_content = st.text_area("Edit Note", note[2], key = f"edit_{note[0]}")
                new_tags = st.multiselect(
                    "Choose Tags for your New Note",
                    st.session_state.init_tags,
                    default = note[4].split(", ") if note[4] else [],
                    key = f"selectU_{note[0]}"
                )
                st.caption(f"⏰ {note[3]}")

                col1, col2 = st.columns([0.26, 0.4])
                if (note[2] != new_content and new_content.strip()) or (note[4] != ", ".join(new_tags)):
                    update_note(note[0], new_content, new_tags)
                    st.rerun()
                with col2:
                    if st.button("❌ Delete", key = f"delete_{note[0]}"):
                        delete_note(note[0])
                        st.rerun()
