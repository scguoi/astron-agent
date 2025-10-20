# AstronAgent Complete Deployment Guide

This guide will help you start all components of the AstronAgent project in the correct order, including identity authentication, knowledge base, and core services.

## 📋 Project Architecture Overview

The AstronAgent project consists of the following three main components:

1. **Casdoor** - Identity authentication and single sign-on service (required component for SSO functionality)
2. **RagFlow** - Knowledge base and document retrieval service (optional component, deploy as needed)
3. **AstronAgent** - Core business service cluster (required component)

## 🚀 Deployment Steps

### Prerequisites

**Agent System Requirements**
- CPU >= 2 Core
- RAM >= 4 GiB
- Disk >= 50 GB

**RAGFlow Requirements**
- CPU >= 4 Core
- RAM >= 16 GB
- Disk >= 50 GB

### Step 1: Start Casdoor Identity Authentication Service

Casdoor is an open-source Identity and Access Management (IAM) platform that supports multiple authentication protocols including OAuth 2.0, OIDC, and SAML.

To start Casdoor service, run our [docker-compose.yaml](/docker/casdoor/docker-compose.yaml) file. Before running the installation command, ensure that Docker and Docker Compose are installed on your machine.

```bash
# Navigate to Casdoor directory
cd docker/casdoor

# Create logs directory for mounting
mkdir -p logs

# Set permissions for logs directory
chmod -R 777 logs

# Start Casdoor service
docker-compose up -d

# Check service status
docker-compose ps

# View logs
docker-compose logs -f
```

**Service Information:**
- Access URL: http://localhost:8000
- Container name: casdoor
- Default configuration: Production mode (GIN_MODE=release)

**Configuration Directories:**
- Configuration files: `./conf` directory
- Log files: `./logs` directory

### Step 2: Start RagFlow Knowledge Base Service (Deploy as Needed)

RagFlow is an open-source RAG (Retrieval-Augmented Generation) engine that provides accurate question-answering services using deep document understanding technology.

To start RagFlow service, run our [docker-compose.yml](/docker/ragflow/docker-compose.yml) file or [docker-compose-macos.yml](/docker/ragflow/docker-compose-macos.yml). Before running the installation command, ensure that Docker and Docker Compose are installed on your machine.

```bash
# Navigate to RagFlow directory
cd docker/ragflow

# Add executable permissions to all sh files
chmod +x *.sh

# Start RagFlow service (including all dependencies)
docker compose up -d

# Check service status
docker compose ps

# View service logs
docker compose logs -f ragflow
```

**Access URL:**
- RagFlow Web Interface: http://localhost:10080

**Model Configuration Steps:**
1. Click the avatar to enter the **Model Providers** page, select **Add Model**, fill in the corresponding **API URL** and **API Key**, and add both **Chat Model** and **Embedding Model** respectively.
2. In the upper right corner of the same page, click **Set Default Models** and set the **Chat Model** and **Embedding Model** added in step 1 as default.


**Important Configuration Notes:**
- Elasticsearch is used by default. To use opensearch or infinity, modify the DOC_ENGINE configuration in .env
- GPU acceleration is supported using `docker-compose-gpu.yml`

### Step 3: Integration Configuration for Casdoor and RagFlow Services (Configure as Needed)

Before starting AstronAgent services, configure the connection information to integrate with Casdoor and RagFlow.

```bash
# Navigate to astronAgent directory
cd docker/astronAgent

# Copy environment variables configuration
cp .env.example .env
```

#### 3.1 Configure Knowledge Base Service Connection

Edit the docker/astronAgent/.env file to configure RagFlow connection information:

```bash
# Navigate to astronAgent directory
cd docker/astronAgent

# Edit environment variables configuration
vim .env
```

**Key Configuration Items:**

```env
# RAGFlow Configuration
RAGFLOW_BASE_URL=http://localhost:10080
RAGFLOW_API_TOKEN=ragflow-your-api-token-here
RAGFLOW_TIMEOUT=60
RAGFLOW_DEFAULT_GROUP=Astron Knowledge Base
```

**Obtaining RagFlow API Token:**
1. Access RagFlow Web Interface: http://localhost:10080
2. Log in and click the avatar to enter user settings
3. Click API to generate an API KEY
4. Update the generated API KEY to RAGFLOW_API_TOKEN in the .env file

#### 3.2 Configure Casdoor Authentication Integration

Edit the docker/astronAgent/.env file to configure Casdoor connection information:

**Key Configuration Items:**

```env
# Casdoor Configuration
CONSOLE_CASDOOR_URL=http://your-casdoor-server:8000
CONSOLE_CASDOOR_ID=your-casdoor-client-id
CONSOLE_CASDOOR_APP=your-casdoor-app-name
CONSOLE_CASDOOR_ORG=your-casdoor-org-name
```

**Obtaining Casdoor Configuration Information:**
1. Access Casdoor management console: [http://localhost:8000](http://localhost:8000)
2. Log in with the default administrator account: `admin / 123`
3. **Create Organization**
   Navigate to [http://localhost:8000/organizations](http://localhost:8000/organizations), click "Add", fill in the organization name, then save and exit.
4. **Create Application and Bind Organization**
   Navigate to [http://localhost:8000/applications](http://localhost:8000/applications), click "Add".

   Fill in the following information when creating the application:
   - **Name**: Custom application name, e.g., `agent`
   - **Redirect URL**: Set to the project's callback address, e.g., `http://your-local-ip:80/callback`
     (This address is the callback port for the Nginx container in the project, default `80`)
   - **Organization**: Select the organization name just created
5. After saving the application, record the following information and map it to the project configuration items:

| Casdoor Information Item | Example Value | Corresponding Configuration Item in `.env` |
|--------------------------|---------------|-------------------------------------------|
| Casdoor Service URL | `http://localhost:8000` | `CONSOLE_CASDOOR_URL=http://localhost:8000` |
| Client ID | `your-casdoor-client-id` | `CONSOLE_CASDOOR_ID=your-casdoor-client-id` |
| Application Name | `your-casdoor-app-name` | `CONSOLE_CASDOOR_APP=your-casdoor-app-name` |
| Organization Name | `your-casdoor-org-name` | `CONSOLE_CASDOOR_ORG=your-casdoor-org-name` |

6. Fill in the above configuration information into the project's environment variable file: docker/astronAgent/.env
```bash
# Navigate to astronAgent directory
cd docker/astronAgent

# Edit environment variables configuration
vim .env
```


### Step 4: Start AstronAgent Core Services (Required Deployment Step)

#### 4.1 Configure iFLYTEK Open Platform APP_ID, API_KEY, and Other Information

For documentation on obtaining these, see: https://www.xfyun.cn/doc/platform/quickguide.html

After creating the application, you may need to purchase or claim API authorization service volume for the corresponding capabilities:
- Spark LLM API: https://xinghuo.xfyun.cn/sparkapi
  (For LLM API, there is an additional SPARK_API_PASSWORD that needs to be obtained from the page)
- Real-time Speech Transcription API: https://www.xfyun.cn/services/rtasr
- Image Generation API: https://www.xfyun.cn/services/wtop

Finally, edit the docker/astronAgent/.env file to update the relevant environment variables:
```env
PLATFORM_APP_ID=your-app-id
PLATFORM_API_KEY=your-api-key
PLATFORM_API_SECRET=your-api-secret

SPARK_API_PASSWORD=your-api-password
SPARK_RTASR_API_KEY=your-rtasr-api-key
```

#### 4.2 If You Want to Use Spark RAG Cloud Service, Configure as Follows

Spark RAG Cloud Service provides two usage methods:

##### Method 1: Obtain from the Web Page

1. Use the APP_ID and API_SECRET created on the iFLYTEK Open Platform
2. Obtain the Spark dataset ID directly from the page, see: [xinghuo_rag_tool.html](/docs/xinghuo_rag_tool.html)

##### Method 2: Use cURL Command Line

If you prefer using command-line tools, you can create a dataset with the following cURL command:

```bash
# Create Spark RAG dataset
curl -X PUT 'https://chatdoc.xfyun.cn/openapi/v1/dataset/create' \
    -H "Accept: application/json" \
    -H "appId: your_app_id" \
    -H "timestamp: $(date +%s)" \
    -H "signature: $(echo -n "$(echo -n "your_app_id$(date +%s)" | md5sum | awk '{print $1}')" | openssl dgst -sha1 -hmac 'your_api_secret' -binary | base64)" \
    -F "name=My Dataset"
```

**Notes:**
- Replace `your_app_id` with your actual APP ID
- Replace `your_api_secret` with your actual API Secret

After obtaining the dataset ID, update it to the docker/astronAgent/.env file:
```env
XINGHUO_DATASET_ID=
```

#### 4.3 Start AstronAgent Services

Before starting, configure some required environment variables and ensure that nginx and minio ports are open.

```bash
# Navigate to astronAgent directory
cd docker/astronAgent

# Modify configuration as needed
vim .env
```

```env
HOST_BASE_ADDRESS=http://localhost (AstronAgent service host address)
```

To start AstronAgent services, run our [docker-compose.yaml](/docker/astronAgent/docker-compose.yaml) file. Before running the installation command, ensure that Docker and Docker Compose are installed on your machine.

```bash
# Navigate to astronAgent directory
cd docker/astronAgent

# Start all services
docker compose up -d

# Check service status
docker compose ps

# View service logs
docker compose logs -f
```

## 📊 Service Access Addresses

After startup is complete, you can access various services through the following addresses:

### Authentication Service
- **Casdoor Management Interface**: http://localhost:8000

### Knowledge Base Service
- **RagFlow Web Interface**: http://localhost:10080

### AstronAgent Core Services
- **Console Frontend (nginx proxy)**: http://localhost/

## 📚 More Resources

- [AstronAgent Official Documentation](https://docs.astronAgent.cn)
- [Casdoor Official Documentation](https://casdoor.org/docs/overview)
- [RagFlow Official Documentation](https://ragflow.io/docs)
- [Docker Compose Official Documentation](https://docs.docker.com/compose/)

## 🤝 Technical Support

If you encounter issues, please:

1. Check the log files of related services
2. Review official documentation and troubleshooting guides
3. Submit an Issue in the project's GitHub repository
4. Contact the technical support team

---

**Note**: For first-time deployment, it is recommended to verify all functionalities in a test environment before deploying to production.
