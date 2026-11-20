"""Public HR demonstration. The role chooser is a simulation, not login."""
import logging
import os
import streamlit as st
from usage import reserve_request, DemoLimit

def render():
    st.markdown(
        '<section class="hero"><div class="eyebrow">AEGIS AI ADVISORY / LIVE SAMPLE</div>'
        '<h1>Ask HR.<br><span>Find the policy.</span></h1>'
        '<p>Search current employee policies with source citations, '
        'role-specific document access and a handoff when a person is needed.</p>'
        '<div class="hero-note">FICTIONAL COMPANY <span>·</span> WORD + PDF</div>'
        '</section>', unsafe_allow_html=True)
    st.info("Fictional Northwoods Professional Services sample. Role selection demonstrates "
            "filtering; it is NOT authentication. Do not enter real employee or confidential data.")
    st.caption("Aegis AI Advisory · Practical AI. Human oversight.")
    if "hr_question" not in st.session_state:
        st.session_state.hr_question = ""
    def reset():
        st.session_state.pop("hr_result",None)
    def sample(text):
        st.session_state.hr_question = text
        reset()
    left,right=st.columns([1.7,1],gap="large")
    with left:
        role=st.selectbox("Illustrative role (not a login)",["Employee","HR administrator"],
                          key="hr_role",on_change=reset)
        role_key="hr" if role=="HR administrator" else "employee"
        with st.form("hr_query"):
            question=st.text_area("Question about your workplace policy",
                                  key="hr_question",height=110,max_chars=1000)
            submitted=st.form_submit_button("Check current policies →",type="primary",
                                            use_container_width=True)
        st.markdown("**Try an example**")
        for label,prompt in [
            ("Learning budget","What is the current professional development allowance?"),
            ("Paid time off","How many paid days off do full-time employees receive?"),
            ("Remote work","Can employees work remotely?"),
            ("Sensitive question → HR","I want to report harassment."),
            ("Unanswered → HR","Can I bring my dog to the office?"),
        ]:
            st.button(label,on_click=sample,args=(prompt,),key="hr_"+label,
                      use_container_width=True)
    with right:
        with st.container(border=True):
            st.subheader("Current document library")
            st.markdown("**Employee Handbook · v2.0**")
            st.caption("Word · approved · remote work, training, reporting")
            st.markdown("**Time Off Policy · v3.0**")
            st.caption("PDF · approved · vacation, sick time, holidays")
            st.markdown("**HR Procedures · v1.0**")
            st.caption("Markdown · HR audience only in this simulation")
            st.markdown("**Employee Handbook · v1.0**")
            st.caption("Superseded and excluded (old $300 training limit)")
        with st.expander("What this demonstrates"):
            st.write("The active handbook increased the training budget to $600. "
                     "The prior $300 version is never indexed. Each answer shows the "
                     "active policy version, section, and exact quote.")
            st.write("In a real deployment, roles would be verified with SSO, HR cases "
                     "would go to a configured person, and every customer would have "
                     "a separate private document store.")
        with st.expander("Inspect actual source files"):
            st.link_button("Word handbook", "https://github.com/dblomqu1-8980/aegis-policy-qa/blob/main/data/hr/employee-handbook-v2.docx")
            st.link_button("PDF time-off policy", "https://github.com/dblomqu1-8980/aegis-policy-qa/blob/main/data/hr/time-off-policy-v3.pdf")
    if submitted:
        reset()
        if not question.strip():
            st.warning("Enter a sample question.")
        else:
            try:
                if not os.getenv("OPENAI_API_KEY"):
                    try: st.secrets.get("OPENAI_API_KEY")
                    except FileNotFoundError: pass
                reserve_request(st.session_state)
                from hr_engine import ask_hr
                with st.spinner("Checking the current policy…"):
                    result=ask_hr(question.strip(),role=role_key)
                st.session_state.hr_result=(role_key,question.strip(),result)
            except DemoLimit as error:
                st.warning(str(error))
            except Exception as error:
                logging.getLogger("aegis").error("HR sample failed: %s",type(error).__name__)
                st.error("The assistant is temporarily unavailable.")
    if "hr_result" in st.session_state:
        previous_role,q,result=st.session_state.hr_result
        if previous_role==role_key:
            st.divider()
            with st.container(border=True):
                st.caption("SAMPLE QUESTION")
                st.write(q)
                st.subheader("Human escalation" if result.get("escalation") else "Current policy answer")
                st.write(result["answer"])
                if result.get("escalation"):
                    st.caption("Demo only: no real HR email or ticket was sent.")
            for i,c in enumerate(result["citations"],1):
                with st.container(border=True):
                    st.markdown(f'**Source {i}: {c["title"]}**')
                    st.caption(f'Section {c["section"]} · v{c["version"]} · effective {c["effective_date"]}')
                    st.write("“"+c["quote"]+"”")
                    st.link_button("Open original document",c["source"])
    st.divider()
    st.markdown("**Want one for your business?** [Talk to Aegis AI Advisory]"
                "(https://www.aegisaiadvisory.com/contact/)")
    st.caption("Fictional educational demonstration only. Not HR or legal advice.")
