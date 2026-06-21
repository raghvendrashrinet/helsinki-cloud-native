import streamlit as st

st.title("Hello from Streamlit! 🎈")
st.write("This entire single-page site was built using pure Python.")

# Let's add an interactive button just for fun
if st.button("Click to see a message"):
    st.success("You clicked the button! No JavaScript or HTML required.")
