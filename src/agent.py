from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.agents import create_tool_calling_agent, AgentExecutor
from langchain.tools import tool
from src.tools import DiagramBuilder, NODE_TYPE_MAP
from src.config import settings


def run_agent(user_prompt: str) -> str:
    """
    Executes the full agentic workflow for a single user request.
    This function is designed to be fully stateless.
    """
    with DiagramBuilder() as builder:
        @tool
        def add_node(label: str, node_type: str) -> str:
            """
            Adds a new node to the diagram.
            'label' is the display name of the node and must be unique.
            'node_type' must be one of the supported types.
            Returns the unique ID of the created node (its label).
            """
            return builder.add_node(label, node_type)

        @tool
        def link_nodes(from_node_id: str, to_node_id: str):
            """
            Connects two nodes with a directed arrow.
            Use the unique IDs (labels) returned by the 'add_node' tool.
            """
            builder.link_nodes(from_node_id, to_node_id)

        @tool
        def render_diagram() -> str:
            """
            Finalizes the diagram creation. This MUST be the last tool called.
            Returns the path to the generated image file.
            """
            return builder.render_diagram()

        tools = [add_node, link_nodes, render_diagram]

        llm = ChatGoogleGenerativeAI(
            model="gemini-2.0-flash-lite",
            google_api_key=settings.GEMINI_API_KEY,
            temperature=0.0
        )

        available_nodes = ", ".join(NODE_TYPE_MAP.keys())

        prompt_template = ChatPromptTemplate.from_messages([
            ("system", f"""You are an expert solutions architect. Your goal is to create a logically complete and useful diagram based on the user's request.

            You MUST follow these rules:
            1.  **Think expansively**: If a user asks for a simple component like 'a web server', you must infer a complete, logical context (e.g., user, load balancer, servers, database).
            2.  **Plan your work**: First, think step-by-step about all the nodes you need. Second, think about how to link them.
            3.  **Execute in order**: First, call `add_node` for ALL necessary nodes. Only after all nodes are added, call `link_nodes` to connect them.
            4.  **Finish the job**: You MUST finish your work by calling the `render_diagram` tool. This must be the final action.
            5.  **No questions**: Do not ask for clarification. Make reasonable, expert assumptions.
            6.  **Use available nodes**: You can ONLY use the following 'node_type' values: {available_nodes}. Do not invent new types.
            7.  **Final Output**: After calling `render_diagram`, your work is complete. Your final answer MUST be ONLY the file path returned by the `render_diagram` tool. Do not add any other text, explanation, or summary.
            """),
            ("human", "{input}"),
            MessagesPlaceholder(variable_name="agent_scratchpad"),
        ])

        agent = create_tool_calling_agent(llm, tools, prompt_template)
        agent_executor = AgentExecutor(agent=agent, tools=tools, verbose=True)

        result = agent_executor.invoke({"input": user_prompt})

        return result.get('output', '').strip()
