# 🔐 Personal Document Vault
### A cloud-based document management application built with Flask and AWS

[![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![Flask](https://img.shields.io/badge/Backend-Flask-000000?logo=flask&logoColor=white)](https://flask.palletsprojects.com/)
[![Amazon S3](https://img.shields.io/badge/Storage-Amazon%20S3-569A31?logo=amazons3&logoColor=white)](https://aws.amazon.com/s3/)
[![Amazon RDS](https://img.shields.io/badge/Database-Amazon%20RDS-527FFF?logo=amazonrds&logoColor=white)](https://aws.amazon.com/rds/)
[![Amazon EC2](https://img.shields.io/badge/Compute-Amazon%20EC2-FF9900?logo=amazonec2&logoColor=white)](https://aws.amazon.com/ec2/)

**Personal Document Vault** is a Flask web application for uploading, organizing, searching, downloading, and deleting personal documents. It separates application hosting, file storage, and relational metadata across AWS services.

> **Deployment note:** The project has been configured and deployed to AWS for testing. EC2 and RDS are currently stopped when not needed to help control costs. Verify live availability, DNS, and HTTPS certificate status before a demonstration.

---

## 📌 Table of contents
- [Project overview](#-project-overview)
- [Features](#-features)
- [Technology stack and AWS services](#-technology-stack-and-aws-services)
- [Architecture](#-architecture)
- [How it works](#-how-it-works)
- [Database design](#-database-design)
- [Run locally](#-run-locally)
- [AWS deployment overview](#-aws-deployment-overview)
- [Security considerations](#-security-considerations)
- [Repository structure](#-repository-structure)
- [Cost management](#-cost-management)
- [Future improvements](#-future-improvements)

## 🎯 Project overview

Personal files can become scattered across devices and folders. This project provides an authenticated web interface for maintaining a personal document library.

### Objectives
- Provide registration and login.
- Upload supported documents and organize them by category.
- Store files in Amazon S3 and metadata in MySQL.
- Restrict document operations to the authenticated owner.
- Demonstrate cloud compute, object storage, relational database, and access-management services.

## ✨ Features

- **Account access:** Registration, login, and session-based authentication.
- **Dashboard:** Document summaries and recent uploads.
- **Document upload:** PDF, JPG, JPEG, and PNG, subject to application validation rules.
- **Organization:** Search by document name and filter by category.
- **Download:** Short-lived S3 presigned URLs.
- **Deletion:** Remove the S3 object and associated metadata through the application.
- **Per-user access:** Document queries are scoped to the signed-in user's ID.

## 🧰 Technology stack and AWS services

| Component | Technology / service | Responsibility |
|---|---|---|
| Frontend | HTML, CSS, JavaScript, Jinja | User interface |
| Backend | Python, Flask | Routes, validation, and application logic |
| Application server | Gunicorn | Serves the Flask application |
| Compute | **Amazon EC2** | Runs the web application |
| Object storage | **Amazon S3** | Stores uploaded document files |
| Relational database | **Amazon RDS for MySQL** | Stores user records and document metadata |
| AWS permissions | **AWS IAM instance role** | Grants permitted AWS access without hard-coded long-term keys |
| Networking | Amazon VPC and security groups | Network environment and traffic rules |
| Domain | DuckDNS | Maps a domain to the current public IP |
| Encrypted web access | HTTPS/TLS configuration | Encrypts browser-to-server traffic when correctly configured |

> **Scope note:** An Elastic Load Balancer, CloudWatch monitoring, Lambda, API Gateway, and Cognito are not described as deployed project components here. Treat them as future options unless separately configured and verified.

## 🏗️ Architecture

```text
                         ┌─────────────────────┐
                         │ User's web browser  │
                         └──────────┬──────────┘
                                    │ HTTP(S)
                                    ▼
                         ┌─────────────────────┐
                         │ Amazon EC2          │
                         │ Flask + Gunicorn    │
                         └───────┬───────┬─────┘
                                 │       │
                       SQL / metadata   │ File operations
                                 │       │
                                 ▼       ▼
                       ┌────────────┐ ┌────────────┐
                       │ Amazon RDS │ │ Amazon S3  │
                       │ MySQL      │ │ Documents  │
                       └────────────┘ └────────────┘

                 AWS IAM role authorizes EC2's AWS access
```

### Why these services?
- **EC2** runs the application and handles incoming requests.
- **S3** stores document objects separately from database records.
- **RDS for MySQL** stores structured records and relationships.
- **IAM** controls which AWS actions the application can perform.
- **VPC and security groups** help control network access.

## 🔄 How it works

1. **Register and sign in:** The application processes the form and uses its authentication logic and database records.
2. **Upload:** Flask receives the file and checks it against the application's validation rules.
3. **Store in S3:** The backend uses Boto3 and its configured AWS identity to upload the object.
4. **Save metadata in RDS:** MySQL stores information such as document name, category, owner, content type, size, and S3 object key.
5. **List and filter:** Flask queries metadata for the signed-in user and renders the results.
6. **Download:** The application checks ownership and can generate a time-limited presigned URL for the S3 object.
7. **Delete:** The application removes the S3 object and its database record according to the implemented route logic.

## 🗃️ Database design

The schema is defined in `schema.sql`.

- **`users`**: user ID, name, email, password hash, and creation timestamp.
- **`documents`**: document ID, owner/user ID, display name, category, S3 object key, content type, file size, and creation timestamp.

Apply the schema to a configured MySQL database:

```bash
mysql -h <rds-endpoint> -u <database-user> -p < schema.sql
```

Replace placeholders with your own connection details. Never publish database passwords.

## 💻 Run locally

### Prerequisites
- Python 3.10 or later
- Access to a MySQL database
- An AWS identity with the required S3 permissions for cloud-storage features

### Setup

1. Clone the repository:

   ```bash
   git clone https://github.com/Code-Crack-cpu/personal-document-vault-aws.git
   cd personal-document-vault-aws
   ```

2. Create and activate a virtual environment:

   **Windows PowerShell**
   ```powershell
   python -m venv .venv
   .\.venv\Scripts\Activate.ps1
   ```

   **macOS / Linux**
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   ```

3. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

4. Copy `.env.example` to `.env` and fill in the required local configuration values.
5. Create the tables using `schema.sql`.
6. Configure AWS credentials through a suitable local AWS profile or credential provider. **Never commit credentials or a real `.env` file.**
7. Start the application with `python run.py` and open `http://127.0.0.1:5000` if that is the configured port.

## ☁️ AWS deployment overview

The deployment pattern for this project is:

1. Create an S3 bucket with Block Public Access and appropriate encryption settings.
2. Configure an RDS for MySQL database in the intended AWS network.
3. Apply `schema.sql` to create the tables.
4. Deploy the Flask project and dependencies to EC2.
5. Attach an IAM instance role with only the S3 permissions the application requires.
6. Configure environment variables without embedding secrets in source code.
7. Run the application using Gunicorn.
8. Configure DNS and HTTPS separately, then verify the domain, certificate, and application routes.

Verify exact security-group rules, certificate tooling, and current deployment status in the AWS Console before presenting them as production-ready.

## 🔒 Security considerations

- Store password hashes, not plaintext passwords.
- Use parameterized SQL queries.
- Keep the S3 bucket private.
- Generate presigned URLs only after checking document ownership.
- Validate file type and size on the server.
- Use IAM roles rather than long-lived AWS keys on EC2.
- Limit database network access to resources that need it.
- Keep `.env`, private keys, credentials, and real documents out of Git.
- HTTPS depends on a valid certificate, correct DNS, and server configuration.

## 📁 Repository structure

```text
app/
  models/                 Database model/data-access helpers
  routes/                 Authentication, dashboard, and document routes
  __init__.py              Flask application setup
  config.py                Environment-backed configuration
  db.py                    Database connection/query helpers
  storage.py               S3 operations
templates/                 Jinja HTML templates
  auth/                    Login and registration templates
static/                    CSS and JavaScript
schema.sql                 MySQL database schema
run.py                     Application entry point
requirements.txt            Python dependencies
.env.example                Example configuration keys (no real secrets)
README.md                   Project documentation
```

## 💰 Cost management

- Stop EC2 when it is not needed; compute billing pauses while the instance is stopped.
- RDS can be stopped temporarily, but storage and backup charges may continue and AWS automatically restarts a stopped instance after its allowed stop period.
- EBS volumes and S3 objects continue to incur storage charges.
- Review AWS Billing and Cost Explorer regularly.
- Do not create an Elastic Load Balancer solely to change the EC2 public IP; it adds cost and is unnecessary for this single-instance setup.
- If EC2's automatically assigned public IP changes after restart, update DuckDNS and verify DNS/HTTPS.

## 🚀 Future improvements

- Add CSRF protection, email verification, and password reset.
- Add pagination and upload progress indicators.
- Add structured logging, CloudWatch alarms, and monitoring if configured.
- Automate HTTPS certificate renewal and deployment checks.
- Add document previews, explicit sharing controls, and optional malware scanning.

---

## 📚 Project links

- **GitHub repository:** https://github.com/Code-Crack-cpu/personal-document-vault-aws
- **Amazon EC2:** https://aws.amazon.com/ec2/
- **Amazon S3:** https://aws.amazon.com/s3/
- **Amazon RDS:** https://aws.amazon.com/rds/
- **AWS IAM:** https://aws.amazon.com/iam/

> Built as a cloud architecture and application deployment project to explore compute, object storage, relational databases, and AWS access management.
