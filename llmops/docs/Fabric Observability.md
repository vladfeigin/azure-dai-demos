# Fabric Deployment Hub

## Overview

The **Fabric** is a Microsoft SaaS platform it'sa  solution to enhance data observability, experimentation, and troubleshooting. It provides:

- **Tracing**: Trace your application's runtime and data pipelines using advanced telemetry-based instrumentation integrated with Microsoft Fabric's tools.
- **Evaluation**: Leverage built-in analytics and AI capabilities to benchmark application performance using custom evaluations and metrics, enabling deeper insights into system performance.
- **Datasets**: Create and manage versioned datasets within the Microsoft Fabric Lakehouse for experimentation, evaluation, and machine learning model fine-tuning, supporting end-to-end workflows.

Fabric seamlessly integrates with Microsoft’s ecosystem, offering a comprehensive suite of tools such as Real-Time Analytics, Data Activator for alerting, and KQL Queryset for advanced querying. 
It provides robust features for organizations looking to build, deploy, and monitor secure and scalable solutions, all within a unified platform.

---

## What

This tool provides:

- **REST APIs** for managing deployments programmatically.
- **Containerized Environment** for easy scalability and deployment.
- **Dynamic Configuration Management** to streamline multi-tenant deployments.
- **Azure Managed Identity Integration** for secure authentication and access control.

### Key Features

- **Scalable Deployments**: Handles large-scale deployment needs.
- **Customizable Configurations**: Uses `appsettings.json` for tenant-specific setups.
- **Secure Authentication**: Integrates with Azure Managed Identities for secure and compliant operations.

![GitHub & DeploymentHub](./images/github-deploymenthub.png)
---

## How

### Prerequisites

- .NET 8.0 SDK
- Docker (for local containerization)
- Azure Subscription with Container Apps enabled
- Configuration values for:
  - `FABRIC_TENANT_CONFIG`
  - `AZURE_TENANT_ID`
  - `FABRIC_API_CLIENT_ID`
  - `FABRIC_API_CLIENT_SECRET`

### Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/your-repository/fabric-deployment-hub.git
2.	Navigate to the project directory:
    ```bash
    cd fabric-deployment-hub
    ```
3. Restore dependencies and build the project:
    ```bash
    dotnet restore
    dotnet build
    ```
### Running Locally

1. Update appsettings.json with your configuration values.
2. Start the application: `dotnet run`
3. Access the APIs at http://localhost:5000.

### Containerization

1. Build the Docker image: `docker build -t fabric-deployment-hub .`
2. Run the container: `docker run -p 5000:80 fabric-deployment-hub`

### Deployment to Azure Container Apps

1. Ensure containerapp-config.json is configured for your environment.
2. Deploy the app using Azure CLI: `az containerapp up --source . --name fabric-deployment-hub --resource-group <your-resource-group>`

## License

This project is licensed under the terms of the MIT License.