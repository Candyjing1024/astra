# Microsoft ASTRA - Deployment Guide

## 🎯 Overview

This document provides step-by-step instructions for deploying the Microsoft ASTRA framework to Azure.

The deployment utilizes GitHub Actions workflows for automated CI/CD, ensuring consistent and reliable deployments across environments.

## 📋 Pre-requisites:
1. Resource Group
2. Service Principal with the following roles assigned to the Resource Group
	a. `Contributor`
	b. `User Access Administrator`
3. Github Repository

## 🚀 Steps for Infra deployment:
1. Add the following as variables in the repository- `AZURE_CICD_CLIENT_ID`, `AZURE_RESOURCE_GROUP_ID`, `AZURE_SUBSCRIPTION_ID`, `AZURE_TENANT_ID`.
2. Add the following as secrets in the repository- `AZURE_CICD_CLIENT_SECRET`.
3. Update the bicep parameters in `astra_core/deploy/parameters/dev/main.bicepparam` as required.
4. Update the run conditions of the workflow as required. By default it is set as `workflow_dispatch` (manual run).
5. Run the `DeployInfra` workflow. This will create all the required Azure components and role assignments as well as the secrets in the key vault and environment variables for the web apps (configured in the bicep).

## 🔧 Steps for backend deployment:
1. Assign the role of `Website Contributor` to the Service Principal on your backend web app.
2. Run the `DeployApp` workflow. This will package all the backend code containing the agentic framework and deploy it to the web app so that the APIs can be accessible through Azure.

## 🎨 Steps for frontend deployment (AGUI):
1. Verify the paths for the `client` and `copilot-runtime-service` that are mentioned in the workflow and update if required.
2. Run the `DeployUI` workflow. This will package all the AGUI components and deploy it to the web app and host the `copilot-runtime-service` endpoint in the back but only expose the user interface endpoint to the user.