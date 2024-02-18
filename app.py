import streamlit as st
import streamlit_authenticator as stauth
import yaml
import re
import base64
from langchain_handler.langchain_qa import (
    validate_environment,
    amazon_bedrock_models,
    amazon_bedrock_llm,
    chain_qa,
    search_and_answer,
)
from data_handlers.doc_source import DocSource, InMemoryAny
from data_handlers.labels import load_labels_master, load_labels
from utils.utils_text import (
    spans_of_tokens_ordered,
    spans_of_tokens_compact,
    spans_of_tokens_all,
    text_tokenizer,
)

# Set page title
st.set_page_config(page_title="Financial Q/A App", layout="wide")


# Set content to center
content_css = """
<style>
    .reportview-container .main .block-container{
        display: flex;
        justify-content: center;
    }
    .stTextArea label p,
    .stSelectbox label p{
        font-size: 18px; 
        font-weight: bold;
    }
    .stHeadingContainer {
        margin-bottom: 30px;
    }
</style>
"""

# Inject CSS with Markdown
st.markdown(content_css, unsafe_allow_html=True)

# Load configuration from a YAML file
with open("config.yml", "r") as file:
    config = yaml.safe_load(file)


authenticator = stauth.Authenticate(
    config['credentials'],
    config['cookie']['name'],
    config['cookie']['key'],
    config['cookie']['expiry_days'],
    config['preauthorized']
)


# Define Streamlit cache decorators for various functions
# These decorators help in caching the output of functions to enhance performance
@st.cache_resource
def check_env():
    # Validate the environment for the langchain QA model
    validate_environment()


@st.cache_data
def list_llm_models():
    models = list(amazon_bedrock_models().keys())
    return models


@st.cache_resource
def create_qa_chain(model_id, verbose=False):
    if model_id in amazon_bedrock_models():
        llm = amazon_bedrock_llm(model_id, verbose=verbose)
    else:
        assert False, f"Unknown {model_id}"

    print("Make QA chain for", model_id)
    print(llm)
    return chain_qa(llm, verbose=verbose)


@st.cache_resource
def list_doc_source_instances():
    return [InMemoryAny(config["corpus"] + config["extension"])]


@st.cache_data
def list_doc_sources():
    return [str(x) for x in list_doc_source_instances()]


def to_doc_source(doc_source_str: str) -> DocSource:
    """String to class instance"""
    return next(i for i in list_doc_source_instances() if str(i) == doc_source_str)


@st.cache_data
def list_doc(doc_source_nm):
    doc_source = to_doc_source(doc_source_nm)
    return doc_source.list_doc()


def make_doc_store(doc_source_nm, doc_path):
    doc_source = to_doc_source(doc_source_nm)
    # Now capturing both values
    store, num_docs = doc_source.make_doc_store(doc_path)
    print(f"Number of documents: {num_docs}")
    # Return both to the caller
    return store, num_docs


@st.cache_data
def load_datapoint_master():
    return load_labels_master(config["datapoint_master"])


@st.cache_data
def list_questions():
    questions = load_datapoint_master()
    questions = ["Ask your question"] + list(questions.values())
    return [f"{i}. {q}" for i, q in enumerate(questions)]


def clean_question(s):
    """Strip heading question number"""
    return re.sub(r"^[\d\.\s]+", "", s)


@st.cache_data
def list_groundtruth(doc_path, question):
    # Find datapoint name
    datapoints = load_datapoint_master()
    # Find Ground Truth for that datapoint for that pdf
    iter_ = (k for k, q in datapoints.items() if q == question)
    datapoint = next(iter_, None)
    ground_truth = load_labels(doc_path, config["datapoint_labels"]).get(
        datapoint, None
    )
    return datapoint, ground_truth


def markdown_bgcolor(text, bg_color):
    return f'<span style="background-color:{bg_color};">{text}</span>'


def markdown_fgcolor(text, fg_color):
    return f":{fg_color}[{text}]"


def markdown_naive(text, tokens, bg_color=None):
    """
    The exact match of answer may not be the possible.
    Split the answer into tokens and find most compact span
    of the text containing all the tokens. Highlight them.
    """
    print("highlight tokens", tokens)

    for t in tokens:
        text = text.replace(t, markdown_bgcolor(t, bg_color))

    # Escaping markup characters
    text = text.replace("$", "\\$")
    return text


def markdown2(text, tokens, fg_color=None, bg_color=None):
    """
    The exact match of answer may not be the possible.
    Split the answer into tokens and find most compact span
    of the text containing all the tokens. Highlight them.
    """
    print("highlight tokens:", tokens)

    spans = []
    if len(tokens) < 20:  # OOM
        spans = spans_of_tokens_ordered(text, tokens)
        if not spans:
            spans = spans_of_tokens_compact(text, tokens)
            print("spans_of_tokens_compact:", spans)
    if not spans:
        spans = spans_of_tokens_all(text, tokens)
        print("spans_of_tokens_all:", spans)

    output, k = "", 0
    for i, j in spans:
        output += text[k:i]
        k = j
        if bg_color:
            output += markdown_bgcolor(text[i:j], bg_color)
        else:
            output += markdown_fgcolor(text[i:j], fg_color)
    output += text[k:]

    return output


def markdown_escape(text):
    """Escaping markup characters"""
    return re.sub(r"([\$\+\#\`\{\}])", "\\\1", text)


def displayPDF(file):
    try:
        # Opening file from file path
        with open(file, "rb") as f:
            base64_pdf = base64.b64encode(f.read()).decode("utf-8")

        # Embedding PDF in HTML
        pdf_display = f'<embed src="data:application/pdf;base64,{base64_pdf}" width="100%" height="850" type="application/pdf">'

        # Displaying File
        st.markdown(pdf_display, unsafe_allow_html=True)
    except Exception as e:
        st.error(f"Failed to display PDF: {e}")
        print(f"Failed to display PDF: {e}")  # For debugging in server logs


def user_authenticate():
    name, authentication_status, username = authenticator.login()
    
    if authentication_status:
        # colL1, colL2 = st.columns([1,12])
        # with colL2:
        #     authenticator.logout('Logout', 'main')
        #     st.write(f'Welcome *{username}*')
        return True, username
    elif authentication_status == False:
        st.error('Username or password is incorrect')
        return None, None
    elif authentication_status == None:
        st.warning('Please enter correct username and password')
        return None, None


# The main function where the Streamlit app logic resides
def main():
    # Ensure the environment is set up correctly
    check_env()

    _, colT2 = st.columns([1,4])
    with colT2:
        st.title("Intelligent Mutual Fund Prospectus Document Processing")

    is_logged_in = None
    
    username = None
    _, col2, _ = st.columns(3)
    with col2:
        is_logged_in, username = user_authenticate()
    
    colL1, colL2 = st.columns([1,4])
    with colL1:
        if is_logged_in:
            st.write(f'##### LoggedIn As : &nbsp;&nbsp;&nbsp;&nbsp;**{username}**')
            authenticator.logout('Logout', 'main')
    
    if is_logged_in:
        # st.title("Intelligent Mutual Fund Prospectus Document Processing")
        
        col1, col2 = st.columns([2.2, 2.0])  # Adjust the ratio as needed

        # Define doc_source_nm early on to ensure it's available when needed
        with col1:  # Right side - Only the full PDF display
            # doc_source_nm = st.selectbox("Select documents source", list_doc_sources())
            doc_source_nm = "InMemoryAny"

            listdocs = list_doc(doc_source_nm)        
            pdf_docs = [doc for doc in listdocs if doc.endswith(".pdf")]

            doc_path = st.selectbox("Select doc", pdf_docs, key="pdf_selector")
            if doc_path.lower().endswith(".pdf"):
                displayPDF(doc_path)

        with col2:  # Left side - All settings and displays except the full PDF
            # Select a language model from the available options
            # model_id = st.selectbox("Select LLM", list_llm_models())
            model_id = "anthropic.claude-v2"

            # Create a QA (Question Answering) chain based on the selected model
            chain_qa = create_qa_chain(model_id, verbose=True)
            prompt_trailer = "Answer in short."

            if (
                st.session_state.get("doc_source_nm", "") != doc_source_nm
                or st.session_state.get("doc_path", "") != doc_path
            ):
                st.empty()

                # Load vector store
                store, num_docs = make_doc_store(doc_source_nm, doc_path)
                st.session_state["doc_source_nm"] = doc_source_nm
                st.session_state["doc_path"] = doc_path
                st.session_state["store"] = store
                st.session_state["num_docs"] = num_docs
            else:
                store = st.session_state["store"]
                num_docs = st.session_state["num_docs"]
                doc_path = st.session_state["doc_path"]

            # Handling user input for the question
            # question = st.selectbox("Select question", [""] + list_questions())
            # question = clean_question(question)

            # Allow user to input a custom question if needed
            # if "Ask" in question:
            question = st.text_area(
                "Your Question: ", placeholder="Ask me anything ...", key="input"
            )

            # Early exit if no question is provided
            if not question:
                return

            # Construct the query by appending a trailer for concise answers
            query = question + " " + prompt_trailer
            query = query.strip()
            print("Q:", query)

            # Display the formatted question
            st.write("**Question**")
            st.text_area(
                label="Preview",
                value=query,
                label_visibility="collapsed",
                height=80,
                disabled=False,
                max_chars=1000,
            )

            # code for processing the query and handling responses
            K = 1
            for attempt in range(4):
                try:
                    response = search_and_answer(
                        store,
                        chain_qa,
                        # prompt_template,
                        query,
                        k=num_docs,
                    )
                    answer = response["response"]
                    break  # Success
                except Exception as e:
                    print(e)
                    st.spinner(text=type(e).__name__)
                    if type(e).__name__ == "ValidationException" and K > 1:
                        print("Retrying using shorter context")
                        K -= 1
                    elif type(e).__name__ == "ThrottlingException":
                        print("Retrying")
                    else:
                        # continue
                        raise e

            print(answer)

            # Display the answer to the user
            if "Helpful Answer:" in answer:
                answer = answer.split("Helpful Answer:")[1]

            # need a double-whitespace before \n to get a newline
            # multiple questions at once
            if "\n" in answer:
                print("Split answer by newline")
                st.write("**Answer**")
                for line in answer.split("\n"):
                    st.text(line)
            else:
                st.write(f"**Answer**: :blue[{answer}]")

            # Load and display ground truth if available
            dp, gt = list_groundtruth(doc_path, question)
            if gt:
                st.markdown(
                    "**Ground truth**: " + markdown_bgcolor(gt, "yellow"),
                    unsafe_allow_html=True,
                )
            else:
                st.write("**Ground truth**: Not available")

            # Highlight and display evidence in the source documents
            tokens_answer = text_tokenizer(answer)
            tokens_labels = text_tokenizer(f"{gt}") if gt else []
            tokens_miss = set(tokens_labels).difference(tokens_answer)

            print("response n_docs", len(response["docs"]))

            # ... [code for marking and displaying the document content]
            for i, doc in enumerate(response["docs"]):
                st.divider()

                markd = doc.page_content

                markd = markdown_escape(markd)

                markd = markdown2(text=markd, tokens=tokens_answer, bg_color="#90EE90")
                markd = markdown2(text=markd, tokens=tokens_miss, bg_color="red")

                print("done")

                st.markdown(markd, unsafe_allow_html=True)


# Call the main function to run the app
main()
