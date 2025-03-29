import streamlit as st

col1_abt, col2_abt = st.columns(2, gap = "small", vertical_alignment = "top")

with col1_abt:
	st.image("images/logo.png", width = 270)
with col2_abt:
	st.subheader("**SHelper** - Your All-in-One Productivity Assistant")
	st.write("**SHelper** is a smart productivity tool that helps you stay organized and achieve your goals.")
	st.subheader("Key Features:")
	st.write("✅ **Notes & Organization** - Create and manage notes with tags.")
	st.write("✅ **Time Management** - Plan tasks efficiently and track deadlines.")
	st.write("✅ **Goal Setting** - Set, track, and achieve your personal and work goals.")
	st.write("**Boost your productivity with SHelper! 🚀**")