# Secure Personal Document Vault

Secure Personal Document Vault is a small Flask web application for storing and organising personal documents in AWS. Users create an account, upload supported files, search and filter their own library, download files through short-lived S3 URLs, and delete documents when they are no longer needed.

> **Project status:** Under development and not yet deployed to AWS. The AWS sections describe the intended deployment architecture only; no EC2, RDS, or S3 resources are created by this repository.

## Problem statement

Important personal files are often scattered across devices and exposed through unstructured cloud folders. This project demonstrates a simple, private document-management workflow backed by AWS managed services.

## Objectives

- Provide registration, login, and session-based authentication.
- Keep uploaded files out of the application server and store them in a private S3 bucket.
- Store only document metadata and S3 object keys in RDS MySQL.
- Demonstrate least-privilege IAM access from an EC2-hosted Flask application.

## Features

- Password-hashed registration and login.
- Dashboard with totals, categories, and recent uploads.
- Upload PDF, JPG, JPEG, and PNG files up to 10 MB.
- Search by document name and filter by category.
- Secure five-minute S3 presigned download URLs.
- Delete both the S3 object and its corresponding database metadata.
- Per-user queries and ownership checks on document actions.

## Technology stack and AWS services

| Layer | Technology |
| --- | --- |
| Frontend | HTML, CSS, vanilla JavaScript |
| Backend | Python Flask |
| Database | MySQL on Amazon RDS |
| File storage | Private Amazon S3 |
| Hosting | Amazon EC2 with Gunicorn |
| Access/monitoring | IAM instance role / optional CloudWatch |

```text
User -> Web Browser -> Amazon EC2 (Flask + Gunicorn)
                              |-> Amazon S3 (private document files)
                              |-> Amazon RDS MySQL (users + metadata)

                         AWS IAM controls EC2 permissions
                         Amazon CloudWatch can monitor logs
```

The browser never receives AWS credentials and the S3 bucket does not need public access. The application generates a temporary URL only after confirming that the requested document belongs to the signed-in user.

## Application workflow

1. A user registers; the password is stored as a Werkzeug password hash.
2. The user signs in and receives a Flask session.
3. Upload validation checks the extension, MIME type, and size, then streams the file to S3 under `users/<user_id>/<uuid>.<extension>`.
4. The server stores the display name, category, content type, size, owner, and S3 object key in RDS.
5. Download and delete routes query by both document ID and session user ID.

## Database design

`users` stores `id`, `name`, `email`, `password_hash`, and `created_at`.

`documents` stores `user_id` (foreign key), `name`, `category`, `object_key`, `content_type`, `file_size`, and `created_at`. The foreign key uses `ON DELETE CASCADE`; the application removes the S3 object before its metadata.

Create the schema with:

```bash
mysql -h <rds-endpoint> -u <user> -p < schema.sql
```

## Local setup

1. Install Python 3.10+ and MySQL (local or development RDS).
2. Create and activate a virtual environment:

   ```bash
   python -m venv .venv
   # Windows PowerShell
   .\.venv\Scripts\Activate.ps1
   ```

3. Install dependencies with `pip install -r requirements.txt`.
4. Copy `.env.example` to `.env` and set the database values, a strong `SECRET_KEY`, AWS region, and private S3 bucket name.
5. Create tables with `schema.sql`.
6. Configure AWS credentials through the AWS CLI profile locally (`aws configure`) or another standard boto3 provider. Never put access keys in `.env`.
7. Start the app with `python run.py` and visit `http://127.0.0.1:5000`.

## AWS deployment steps

1. Create an S3 bucket with Block Public Access and default encryption enabled.
2. Create RDS MySQL in the EC2 VPC/region and permit MySQL traffic only from the EC2 security group.
3. Run `schema.sql` against the RDS endpoint.
4. Create an EC2 instance and install Python, the project, and dependencies.
5. Attach an IAM instance role with only `s3:PutObject`, `s3:GetObject`, and `s3:DeleteObject` for this bucket's `users/*` prefix. Do not create long-lived keys on EC2.
6. Set environment variables from `.env.example` in the EC2 service environment.
7. Run behind Gunicorn: `gunicorn --bind 0.0.0.0:8000 run:app`.
8. Put Nginx or an Application Load Balancer in front for HTTPS. Send logs to CloudWatch as an optional monitoring improvement.

## Security

- Passwords are hashed and never stored in plaintext.
- SQL uses parameterized statements.
- S3 is private; downloads use expiring presigned URLs.
- Files are validated by extension, MIME type, and size.
- Object keys include a UUID and user namespace.
- Every document query is scoped to the authenticated user's ID.
- AWS access is intended to come from an IAM role rather than hardcoded keys.
- `.env`, credentials, and real documents are ignored by Git.

## Project structure

```text
app/
  models/                 MySQL data-access helpers
  routes/                 Authentication, dashboard, and document routes
  config.py               Environment-backed configuration
  db.py                   Parameterized MySQL helpers
  storage.py              S3 helpers
templates/                Jinja pages
static/                   CSS and browser enhancement
schema.sql                RDS MySQL tables
run.py                    Application entry point
requirements.txt          Python dependencies
```

## Future improvements

- Add CSRF protection, email verification, and password reset.
- Add pagination and upload progress.
- Add antivirus scanning with an S3 event pipeline.
- Add CloudWatch alarms, structured logging, and HTTPS deployment automation.
- Add document previews and explicit sharing permissions.
