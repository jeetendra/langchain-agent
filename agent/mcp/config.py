

def load_mcp_config():
    import json
    from pathlib import Path

    config_path = Path(__file__).parent / "mcp_config.json"
    with open(config_path, "r") as f:
        config = json.load(f)
    
    # Ensure MCP_FILESYSTEM_DIR is set in the environment
    import os
    mcp_filesystem_dir = os.getenv("MCP_FILESYSTEM_DIR")
    if not mcp_filesystem_dir:
        raise ValueError("MCP_FILESYSTEM_DIR environment variable is not set.")
    config["mcpServers"]["filesystem"]["args"][1] = mcp_filesystem_dir
    # Ensure the directory exists
    if not Path(mcp_filesystem_dir).exists():
        raise FileNotFoundError(f"The directory {mcp_filesystem_dir} does not exist.")
    # Ensure the directory is absolute
    if not Path(mcp_filesystem_dir).is_absolute():
        raise ValueError(f"The MCP_FILESYSTEM_DIR {mcp_filesystem_dir} must be an absolute path.")
    # Ensure the transport is set to "stdio"
    if config["mcpServers"]["filesystem"]["transport"] != "stdio":
        raise ValueError("The transport for the filesystem MCP server must be set to 'stdio'.")

    return config

def get_mcp_config():
    """Get the MCP configuration."""
    try:
        config = load_mcp_config()
        return config
    except Exception as e:
        raise RuntimeError(f"Failed to load MCP configuration: {str(e)}")
    
mcp_config  = get_mcp_config()