import streamlit as st
from backend import workflow
from langchain_core.messages import  HumanMessage
import uuid


#utilities functions
def generate_thread_id():
   thread_id = uuid.uuid4()
   return thread_id 

def reset_chat():
    thread_id=generate_thread_id()
    st.session_state['thread_id']=thread_id
    add_thread(thread_id)
    st.session_state['messages']=[]

def add_thread(thread_id):
    exist = False   
    for thread in st.session_state['chat_threads']:
        if(thread['thread_id']==thread_id):
            exist=True
            break

    if (exist==False):
        st.session_state['chat_threads'].append({'thread_id':thread_id,'content':thread_id})   



def load_conversation(thread_id):
    state = workflow.get_state(
        config={'configurable':{'thread_id':thread_id}}
    )

    return state.values.get('messages', [])


# session state a dictionary which not reloads(on enter) until u manually refrsh a page 
if 'messages' not in st.session_state:
    st.session_state['messages']=[]

if 'thread_id' not in st.session_state:
    st.session_state['thread_id'] = generate_thread_id()  

if 'chat_threads' not in st.session_state:
    st.session_state['chat_threads']=[]      

add_thread(st.session_state['thread_id'])


# SideBar
st.sidebar.title('khizGPT')

if st.sidebar.button('New Chat'):
     reset_chat()
    
st.sidebar.header('My Conversations')

for thread in st.session_state['chat_threads']:
    if st.sidebar.button(str(thread['content'])):
      st.session_state['thread_id'] = thread['thread_id']
      messages = load_conversation(thread['thread_id'])

      temp_messages=[]
      
      for message in messages:
          if isinstance(message,HumanMessage):
              role='user'
          else:
              role='assistant'    
          temp_messages.append({'role':role,'content':message.content})

      st.session_state['messages']=temp_messages        


# UI

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
                config={'configurable':{'thread_id':st.session_state['thread_id']}},
                stream_mode='messages'
            )
        )

    st.session_state['messages'].append(
        {'role':'assistant','content':ai_message}
    )

