import streamlit as st
from backend import workflow , retrieve_all_threads
from langchain_core.messages import  HumanMessage,AIMessage
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
    if thread_id not in st.session_state['chat_threads']:
        st.session_state['chat_threads'].append(thread_id) 


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
    st.session_state['chat_threads']=retrieve_all_threads()      

add_thread(st.session_state['thread_id'])


# SideBar
st.sidebar.title('khizGPT')

if st.sidebar.button('New Chat'):
     reset_chat()
    
st.sidebar.header('My Conversations')

for thread_id in reversed(st.session_state['chat_threads']):
    
    messages = load_conversation(thread_id)
    if len(messages) == 0:
        continue

    if st.sidebar.button(str(thread_id)):
      st.session_state['thread_id'] = thread_id
      messages = load_conversation(thread_id)

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
        def ai_only_stream():
            for message_chunk, metadata in workflow.stream(
                {'messages':[HumanMessage(content=user_input)]},
                config={'configurable':{'thread_id':st.session_state['thread_id']}},
                stream_mode='messages'
            ):
                if isinstance(message_chunk,AIMessage):
                    yield message_chunk.content

        ai_message=st.write_stream (ai_only_stream()) 

    st.session_state['messages'].append(
        {'role':'assistant','content':ai_message}
    )

