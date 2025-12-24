import os
from azure.cosmos import CosmosClient, exceptions


def get_cosmos_container():
    """
    Connect to Azure Cosmos DB SQL API and return container client.
    
    Uses environment variables:
    - COSMOS_ENDPOINT: Cosmos DB endpoint URL
    - COSMOS_KEY: Cosmos DB primary key
    - COSMOS_DATABASE: Database name
    - COSMOS_CONTAINER: Container name
    
    Returns:
        azure.cosmos.ContainerProxy: Cosmos DB container client
        
    Raises:
        ValueError: If any required environment variable is missing
        exceptions.CosmosHttpResponseError: If connection fails
    """
    # Get environment variables
    endpoint = os.getenv("COSMOS_ENDPOINT")
    key = os.getenv("COSMOS_KEY")
    database = os.getenv("COSMOS_DATABASE")
    container = os.getenv("COSMOS_CONTAINER")
    
    # Validate environment variables
    if not all([endpoint, key, database, container]):
        raise ValueError(
            "Missing required environment variables: "
            "COSMOS_ENDPOINT, COSMOS_KEY, COSMOS_DATABASE, COSMOS_CONTAINER"
        )
    
    # Create Cosmos DB client
    client = CosmosClient(endpoint, credential=key)
    
    # Get database and container
    db = client.get_database_client(database)
    container_client = db.get_container_client(container)
    
    return container_client
