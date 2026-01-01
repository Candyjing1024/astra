<img width="868" height="371" alt="image" src="https://github.com/user-attachments/assets/73057721-5c5f-4d78-916d-3957c7998ee3" />

# Microsoft ASTRA ✨- Agentic AI System for Transformation, Reasoning, and Autonomy

Microsoft ASTRA ✨ is a flagship multi-agentic AI transformation framework designed to accelerate enterprise adoption of autonomous, intelligent agents. ASTRA ✨ is a modularized, product-centric IP that enables scalable orchestration, reasoning, and delivery across diverse business domains.

# Microsoft ASTRA - Deployment Guide

There are two deployement option:
1- Start with Template (main branch)
2- Start with a Business Use case (individual branches)

### 1- Start with Template (main branch):

The deployment utilizes GitHub Actions workflows for automated CI/CD, ensuring consistent and reliable deployments across environments.

###  📋 Pre-requisites:
1. Resource Group
2. Service Principal with the following roles assigned to the Resource Group
	a. `Contributor`
	b. `User Access Administrator`
3. Github Repository

### 🚀 Steps for Infra deployment:
1. Add the following as variables in the repository- `AZURE_CICD_CLIENT_ID`, `AZURE_RESOURCE_GROUP_ID`, `AZURE_SUBSCRIPTION_ID`, `AZURE_TENANT_ID`.
2. Add the following as secrets in the repository- `AZURE_CICD_CLIENT_SECRET`.
3. Update the bicep parameters in `astra_core/deploy/parameters/dev/main.bicepparam` as required.
4. Update the run conditions of the workflow as required. By default it is set as `workflow_dispatch` (manual run).
5. Run the `DeployInfra` workflow. This will create all the required Azure components and role assignments as well as the secrets in the key vault and environment variables for the web apps (configured in the bicep).
6. Optional: [Follow these steps to enable private networking for infrastructure.](PRIVATE_NETWORKING.md)

### 🔧 Steps for backend deployment:
1. Assign the role of `Website Contributor` to the Service Principal on your backend web app.
2. Run the `DeployApp` workflow. This will package all the backend code containing the agentic framework and deploy it to the web app so that the APIs can be accessible through Azure.

### 🎨 Steps for frontend deployment (AGUI):
1. Verify the paths for the `client` and `copilot-runtime-service` that are mentioned in the workflow and update if required.
2. Run the `DeployUI` workflow. This will package all the AGUI components and deploy it to the web app and host the `copilot-runtime-service` endpoint in the back but only expose the user interface endpoint to the user.



### 2- Start with a Business Use case (individual branches):

1- Replace astra_core code with the selected use case under "branches" 
2- Follow the same steps from #1 


# ASTRA is part of Agentic AI transformation offering]

Here are more details


## 🧭[**Agentic AI Tranformation Offering**](https://catalog.ms/CatalogueOffer?Title=Agentic%20AI%20Transformation&OID=2245)

## 🗺️[**ASTRA Pitch Deck**](https://microsoft.sharepoint.com/:p:/t/SATDataAITeam/EZ3VQMeNoshHl2WhRRpPjVUBg5yB93_0_JjgO7i6wMfnfA?e=mnOTZ2)

## 🏗️ Architecture
<img width="2054" height="975" alt="image" src="https://github.com/user-attachments/assets/46724364-d100-49d2-ac8a-d87ea3bf29cd" />


## 👀 Demos
[**Intelligent Portfolio Optimization**](https://microsoft.sharepoint.com/:v:/t/SATDataAITeam/EVezXhNIPi9LsUdJbQTwUlMBA0k8jY609AKxR-wKagemKQ?e=reRzBP)

[**Emails & Call Transcripts Q&A**](https://microsoft.sharepoint.com/:v:/t/SATDataAITeam/EQ_da48kmLdPlQcuAJzchBkBypir-6wNBHYtq6W3hODywg?e=I9mUj0)



# Contributing

This project welcomes contributions and suggestions.  Most contributions require you to agree to a
Contributor License Agreement (CLA) declaring that you have the right to, and actually do, grant us
the rights to use your contribution. For details, visit [Contributor License Agreements](https://cla.opensource.microsoft.com).

When you submit a pull request, a CLA bot will automatically determine whether you need to provide
a CLA and decorate the PR appropriately (e.g., status check, comment). Simply follow the instructions
provided by the bot. You will only need to do this once across all repos using our CLA.

This project has adopted the [Microsoft Open Source Code of Conduct](https://opensource.microsoft.com/codeofconduct/).
For more information see the [Code of Conduct FAQ](https://opensource.microsoft.com/codeofconduct/faq/) or
contact [opencode@microsoft.com](mailto:opencode@microsoft.com) with any additional questions or comments.

## Trademarks

This project may contain trademarks or logos for projects, products, or services. Authorized use of Microsoft
trademarks or logos is subject to and must follow
[Microsoft's Trademark & Brand Guidelines](https://www.microsoft.com/legal/intellectualproperty/trademarks/usage/general).
Use of Microsoft trademarks or logos in modified versions of this project must not cause confusion or imply Microsoft sponsorship.
Any use of third-party trademarks or logos are subject to those third-party's policies.
