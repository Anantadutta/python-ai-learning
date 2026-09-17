from langchain_core.prompts import ChatPromptTemplate, PromptTemplate, MessagesPlaceholder

# Sample data
students = {
    "Ananta": {"English": 86.0, "Maths": 85.0, "OOPs": 96.0},
    "Rohan": {"Maths": 78.0, "Physics": 82.0, "Chemistry": 74.0},
    "Divya": {"Maths": 92.0, "Chemistry": 89.0, "English": 94.0, "OOPs": 91.0},
}

# 1. STATIC PROMPT — never changes
static_prompt = "You are a helpful academic advisor. Be concise and encouraging."

# 2. DYNAMIC PROMPT — built manually with an f-string
def build_dynamic_prompt(name, marks):
    return f"Analyze {name}'s marks: {marks}. What is their strongest subject?"

dynamic_prompt = build_dynamic_prompt("Ananta", students["Ananta"])

# 3. PROMPT TEMPLATE — same as above, but the LangChain way
template = PromptTemplate.from_template(
    "Analyze {name}'s marks: {marks}. What is their strongest subject?"
)
filled_prompt = template.format(name="Rohan", marks=students["Rohan"])

# 4. CHAT PROMPT TEMPLATE — system + user, structured for chat models
chat_template = ChatPromptTemplate.from_messages([
    ("system", "You are a helpful academic advisor. Be concise and encouraging."),
    ("user", "Here are {name}'s marks: {marks}. Should they get extra tutoring?")
])
chat_messages = chat_template.format_messages(name="Divya", marks=students["Divya"])

# 5. MESSAGE PLACEHOLDER — injecting growing chat history
chat_template_with_history = ChatPromptTemplate.from_messages([
    ("system", "You are a helpful academic advisor. Be concise and encouraging."),
    MessagesPlaceholder(variable_name="chat_history"),
    ("user", "{question}")
])

chat_history = [
    ("user", "Tell me about Rohan's marks."),
    ("assistant", "Rohan scored 78 in Maths, 82 in Physics, and 74 in Chemistry. Physics is his strongest subject."),
]

turn2_messages = chat_template_with_history.format_messages(
    chat_history=chat_history,
    question="How does he compare to Divya?"
)