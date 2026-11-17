"""Aegis-branded interface for the sample policy assistant."""
import base64
from pathlib import Path

import streamlit as st

ROOT = Path(__file__).resolve().parents[1]
st.set_page_config(page_title='Policy Q&A | Aegis AI Advisory', page_icon='🛡️', layout='wide')
st.markdown((ROOT / 'assets' / 'app.css').read_text(), unsafe_allow_html=True)
logo = ROOT / 'assets' / 'aegis-logo.jpeg'
logo_html = ''
if logo.exists():
    encoded = base64.b64encode(logo.read_bytes()).decode()
    logo_html = f'<img src="data:image/jpeg;base64,{encoded}" alt="" width="48" height="48">'
st.markdown(f'''<div class="brand-bar"><a class="brand" href="https://www.aegisaiadvisory.com/" target="_blank" rel="noopener noreferrer">{logo_html}<span><strong>Aegis AI Advisory</strong><small>Practical AI. Human oversight.</small></span></a><span class="demo-tag">INTERACTIVE DEMO</span></div>
<section class="hero"><div class="eyebrow">KNOWLEDGE AT WORK</div><h1>Your policy.<br><span>Clearer answers.</span></h1><p>See how an AI assistant can turn approved documents into everyday guidance—with the sources in view.</p><div class="hero-note">POLICY Q&amp;A <span>·</span> FICTIONAL SAMPLE FIRM</div></section>''', unsafe_allow_html=True)

st.session_state.setdefault('policy_question', '')

def choose_question(question):
    st.session_state.policy_question = question
    st.session_state.pop('policy_result', None)

left, right = st.columns([1.8, 1], gap='large')
with left:
    st.markdown('<div class="eyebrow teal">TRY THE ASSISTANT</div>', unsafe_allow_html=True)
    st.subheader('What would you like to know?')
    st.write('Ask about the sample firm’s AI rules, approvals, or responsibilities.')
    with st.form('question'):
        question = st.text_area('Your question', key='policy_question',
            placeholder='Can I paste client information into ChatGPT?', max_chars=1000, height=110)
        submitted = st.form_submit_button('Find an answer →', type='primary', use_container_width=True)
    st.caption('Use fictional examples only. Do not enter client, personal, or confidential information.')
    st.markdown('**Need a starting point?**')
    for label, sample in [
        ('Client information', 'Can I paste client information into ChatGPT?'),
        ('New tool approval', 'What should I do before trying a new AI tool?'),
        ('Human review', 'Can I send an AI-generated client deliverable without human review?'),
        ('Try an unanswered question', 'What is our office holiday schedule?'),
    ]:
        st.button(label, on_click=choose_question, args=(sample,), use_container_width=True)

with right:
    with st.container(border=True):
        st.markdown('<div class="eyebrow teal">THE SAMPLE WORKSPACE</div>', unsafe_allow_html=True)
        st.subheader('Northwoods Professional Services')
        st.write('A fictional firm with three approved reference documents.')
        st.divider()
        st.markdown('**01 · AI acceptable-use policy**')
        st.caption('Approved tools, sensitive data, vendor practices, and review.')
        st.markdown('**02 · Employee handbook**')
        st.caption('Tool approval, inventory, incident reporting, and escalation.')
        st.markdown('**03 · NIST AI RMF excerpts**')
        st.caption('Selected public guidance on governance and measuring risk.')
    with st.expander('How the demo works'):
        st.write('The assistant searches the sample documents, drafts an answer, and displays supporting quotations. If it cannot find enough evidence or validate its citations, it declines.')
        st.write('The passages let you check the answer yourself. A citation does not guarantee that an answer is correct.')
    with st.expander('Privacy and limitations'):
        st.write('Questions and retrieved passages are sent to OpenAI. This app does not intentionally save question history; provider and hosting retention policies apply.')
        st.write('Northwoods is fictional. This is a demonstration, not legal advice. A person maintains the documents, reviews answers, and approves any policy exceptions.')

if submitted:
    if not question.strip():
        st.warning('Enter a question to get started, or choose one of the examples.')
    else:
        st.session_state.pop('policy_result', None)
        try:
            from answer import ask
            with st.spinner('Finding relevant passages and checking the citations…'):
                result = ask(question)
            st.session_state.policy_result = (question.strip(), result)
        except Exception:
            st.error('The assistant is temporarily unavailable. Please try again. If the problem continues, ask the demo owner to check its connection and setup.')

if 'policy_result' in st.session_state:
    answered_question, result = st.session_state.policy_result
    st.divider()
    with st.container(border=True):
        st.caption('YOUR QUESTION')
        st.write(answered_question)
        if result['citations']:
            st.subheader('Here’s what the documents say')
            st.write(result['answer'])
            st.caption('Based on the passages below. Review the sources before acting.')
        else:
            st.subheader('The documents don’t cover that')
            st.write(result['answer'])
    if result['citations']:
        st.subheader('Check the supporting passages')
        st.caption('Each card shows a quoted passage and where it came from.')
        for number, citation in enumerate(result['citations'], 1):
            with st.container(border=True):
                st.markdown(f'**Source {number} · {citation["title"]}**')
                st.caption(citation['section'])
                st.write('“' + citation['quote'] + '”')
                if citation['source'].startswith('https://doi.org/'):
                    st.link_button('View NIST source ↗', citation['source'])
                else:
                    st.caption('Fictional sample document · Northwoods Professional Services')

st.divider()
st.markdown('<div class="footer"><span><strong>Aegis AI Advisory</strong><br>Useful AI, with people in control.</span><a href="https://www.aegisaiadvisory.com/contact/" target="_blank" rel="noopener noreferrer">Explore AI for your business ↗</a></div>', unsafe_allow_html=True)
