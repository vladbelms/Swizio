import pytest
from src.tools import DiagramBuilder, NODE_TYPE_MAP


@pytest.fixture
def builder():
    """Provides a DiagramBuilder instance within its context."""
    with DiagramBuilder() as b:
        yield b


def test_add_node_success(builder):
    """
    Tests if a node is successfully added to the builder's internal state.
    """
    node_id = builder.add_node(label="Test Server", node_type="EC2")
    assert node_id == "Test Server"
    assert "Test Server" in builder.nodes
    assert isinstance(builder.nodes["Test Server"], NODE_TYPE_MAP["EC2"])


def test_add_node_failure_invalid_type(builder):
    """
    Tests if adding a node with an unsupported type correctly raises a ValueError.
    """
    with pytest.raises(ValueError, match="Unsupported node type"):
        builder.add_node(label="Invalid Node", node_type="ImaginaryDB")


def test_link_nodes_success(builder):
    """
    Tests if two existing nodes can be successfully linked.
    """
    builder.add_node(label="User", node_type="User")
    builder.add_node(label="API", node_type="ALB")

    builder.link_nodes(from_node_id="User", to_node_id="API")
    assert True


def test_link_nodes_failure_nonexistent(builder):
    """
    Tests if linking a non-existent node correctly raises a ValueError.
    """
    builder.add_node(label="Node A", node_type="EC2")
    with pytest.raises(ValueError, match="One or both nodes for linking do not exist"):
        builder.link_nodes(from_node_id="Node A", to_node_id="Non-Existent Node")
