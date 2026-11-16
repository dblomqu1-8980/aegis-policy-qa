import streamlit as st
from answer import ask

st.set_page_config(page_title='Aegis Policy Q&A', page_icon='📘')
st.title('Ask the AI Policy')
st.caption('Aegis AI Advisory · Interactive retrieval demonstration')
st.info('Northwoods Professional Services is fictional. Use sample questions only; do not enter client, personal, or confidential information. This is not legal advice.')
st.write('Ask a question about the sample AI policy, employee handbook, or NIST AI Risk Management Framework excerpts.')
with st.form('question'):
    question = st.text_input('Your question', placeholder='Can I paste client data into ChatGPT?', max_chars=1000)
    submitted = st.form_submit_button('Find an answer', type='primary')
if submitted:
    if not question.strip():
        st.warning('Please enter a question.')
    else:
        try:
            with st.spinner('Checking the source documents…'):
                result = ask(question)
            st.subheader('Answer')
            st.write(result['answer'])
            if result['citations']:
                st.subheader('Supporting passages')
                for citation in result['citations']:
                    with st.container(border=True):
                        st.markdown('**' + citation['title'] + ' — ' + citation['section'] + '**')
                        st.write('“' + citation['quote'] + '”')
                        st.caption(citation['source'])
        except Exception:
            st.error('The demo could not answer. Check the API key, network connection, and index setup, then try again.')
