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

    st.session_state['messages'].append({'role':'user','content':user_input})
    with st.chat_message('user'):
       st.text(user_input)
 
    with st.chat_message('assistant'):
        ai_message = st.write_stream(
            message_chunk.content for message_chunk, metadata in workflow.stream(
                {'messages':[HumanMessage(content=user_input)]},
                config={'configurable':{'thread_id':'1'}},
                stream_mode='messages'
            )
        )

    st.session_state['messages'].append(
        {'role':'assistant','content':ai_message}
    )

