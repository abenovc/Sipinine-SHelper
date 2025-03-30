import streamlit as st

about_page = st.Page(
	page = "projects/about_project.py",
	title = "About Project",
	icon = ":material/home:",
	default = True,
)

notes_page = st.Page(
	page = "projects/notes.py",
	title = "Notes",
	icon = ":material/note_alt:",
)

goals_page = st.Page(
	page = "projects/goals.py",
	title = "Goals",
	icon = ":material/flag_check:",
)

schedule_page = st.Page(
	page = "projects/management.py",
	title = "Schedule",
	icon = ":material/schedule:",
)

pg = st.navigation(
	{
		"Info": [about_page],
		"Projects": [notes_page, goals_page, schedule_page],
	}
)

st.logo("images/mini-logo.png", size = "large")

pg.run()
