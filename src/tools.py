import os
import tempfile
import uuid
from diagrams import Diagram
from diagrams.aws.compute import EC2
from diagrams.aws.database import RDS
from diagrams.aws.network import ALB
from diagrams.onprem.client import User
from typing import Type

NODE_TYPE_MAP: dict[str, Type[EC2 | RDS | ALB | User]] = {
    "EC2": EC2,
    "RDS": RDS,
    "ALB": ALB,
    "User": User,
}


class DiagramBuilder:
    """
    A pure state manager for a single diagram instance.
    Implemented as a context manager to guarantee resource allocation and deallocation
    for each stateless API request. It has no knowledge of LangChain tools.
    """

    def __init__(self):
        temp_dir = tempfile.gettempdir()
        base_name = f"diagram_{uuid.uuid4().hex}"

        self.full_path_with_extension = os.path.join(temp_dir, f"{base_name}.png")

        self.path_for_constructor = os.path.join(temp_dir, base_name)

        self.diag_context = None
        self.nodes = {}

    def __enter__(self):
        """Initializes the diagram context."""
        self.diag_context = Diagram(
            "",
            show=False,
            filename=self.path_for_constructor,
            outformat="png"
        )
        self.diag_context.__enter__()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Ensures the diagram context is closed, rendering the file and releasing resources."""
        self.diag_context.__exit__(exc_type, exc_val, exc_tb)

    def add_node(self, label: str, node_type: str) -> str:
        """Adds a node to the current diagram."""
        if node_type not in NODE_TYPE_MAP:
            raise ValueError(f"Unsupported node type: {node_type}.")
        node_class = NODE_TYPE_MAP[node_type]
        self.nodes[label] = node_class(label)
        return label

    def link_nodes(self, from_node_id: str, to_node_id: str):
        """Links two nodes in the current diagram."""
        if from_node_id not in self.nodes or to_node_id not in self.nodes:
            raise ValueError("One or both nodes for linking do not exist.")
        self.nodes[from_node_id] >> self.nodes[to_node_id]

    def render_diagram(self) -> str:
        """Returns the FULL, ABSOLUTE path (with extension) to the final rendered diagram."""
        return self.full_path_with_extension
