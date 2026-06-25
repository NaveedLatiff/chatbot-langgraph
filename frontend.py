import streamlit as st
from backend import workflow
from langchain_core.messages import  HumanMessage

# session state a dictionary which not reloads(on enter) until u manually refrsh a page 

if 'messages' not in st.session_state:
    st.session_state['messages']=[]



for message in st.session_state['messages']:
    with st.chat_message(message['role']):
        st.text(message['content'])
    

user_input=st.chat_input('Type here')

if (user_input):

    st.session_state['messages'].append({'role':'u  ser','content':user_input})
    with st.chat_message('user'):
       st.text(user_input)


    response=workflow.invoke({'messages':[HumanMessage(content=user_input)]},config={'configurable':{'thread_id':'1'}})
    ai_message=response['messages'][-1].content
    st.session_state['messages'].append({'role':'assistant','content':ai_message})
    with st.chat_message('assistant'):
       st.text(ai_message)   


