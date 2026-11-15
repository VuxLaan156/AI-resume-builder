# AI Resume Builder

## 1. Project Overview

AI Resume Builder is a multi-user, AI-powered application that helps
users create tailored resumes for specific job opportunities. Users
maintain a structured professional profile, upload supporting documents,
provide a target job description (JD), and select a resume template. The
system uses Retrieval-Augmented Generation (RAG) to retrieve relevant
information from the user's background and generate a resume aligned
with the target role.

The application is designed to make resume creation more efficient while
keeping the generated content grounded in the user's actual
qualifications and experience. It must not invent skills, employment
history, projects, education, or certifications.

## 2. Project Objectives

-   Allow multiple users to register and manage their own accounts and
    professional profiles.
-   Store structured information about skills, work experience,
    projects, education, and certifications.
-   Accept uploaded personal documents and job description documents.
-   Extract and organize information from uploaded documents.
-   Use semantic retrieval to find relevant evidence for a target job.
-   Generate resumes tailored to a job description and a selected
    template.
-   Preserve generated resume content and, in a future extension,
    maintain version history.
-   Track document processing and resume-generation tasks.

## 3. Target Users

The system is intended for individuals who want to create or customize
resumes for job applications. Each user has an independent account and
should only be able to access their own profile, uploaded documents, job
descriptions, and resumes.

## 4. Main Features

### 4.1 User and Profile Management

Users can create an account and maintain a professional profile
containing personal and career information.

The profile may include: - Contact information and professional
summary. - Skills and proficiency information. - Work experience. -
Projects. - Education. - Certifications.

The structured profile in PostgreSQL is the main source of truth for the
user's professional information.

### 4.2 Document Upload and Processing

Users can upload documents in supported formats, such as PDF or DOCX.
Documents are managed through a common `Document` entity rather than
separate upload entities for each document category.

Two main document categories are planned:

-   **Personal information documents:** Existing resumes, certificates,
    academic transcripts, project descriptions, and other files
    containing information about the user.
-   **Job description documents:** Files containing a target position's
    responsibilities, requirements, and qualifications.

The document-processing pipeline is expected to: 1. Store the original
file and its metadata. 2. Extract text from the file. 3. Divide the
extracted text into smaller chunks. 4. Generate embeddings for the
chunks. 5. Store vector data and associated payloads in Qdrant. 6.
Extract structured information where appropriate. 7. Associate extracted
information with the relevant profile entities or a structured job
description.

Extracted information should be reviewed or validated before it changes
the user's structured profile. The system should preserve traceability
to the source document.

### 4.3 Job Description Management

A job description can be created from an uploaded JD document or, if
supported by the application, entered manually.

The structured job description may contain: - Job title. - Company
name. - Job description and requirements. - A reference to the original
source document, when applicable.

The JD is used to identify relevant skills, qualifications, and
experience for resume customization.

### 4.4 RAG-Based Information Retrieval

The system uses Retrieval-Augmented Generation to find relevant
information from a user's professional background.

At a high level: 1. The target JD is analyzed. 2. Relevant profile
information and document chunks are retrieved. 3. Retrieved evidence is
supplied to the language model as context. 4. The model generates resume
content grounded in that evidence. 5. The generated content can be
checked for relevance and unsupported claims.

Qdrant is used for vector storage and semantic retrieval. PostgreSQL
remains responsible for structured application data and relationships.

### 4.5 Resume Generation and Templates

Users can select a resume template and generate a resume for a
particular job description.

A resume is associated with: - The user who owns it. - The target job
description, when applicable. - The selected resume template. - The
generated resume content. - The generation timestamp and status.

The system should support reviewing and exporting the generated resume.
PDF export is part of the intended application workflow.

### 4.6 Future Extensions

The following capabilities are recommended extensions and are not
assumed to be implemented in the initial database design:

-   **Resume versioning:** Store each generated or edited version so
    older resumes remain unchanged when a profile is updated.
-   **Generation-job tracking:** Track stages and statuses such as
    pending, processing, completed, or failed.
-   **Improved review and validation:** Identify unsupported claims and
    allow users to correct extracted information.
-   **Additional document categories:** Extend document classification
    without creating a separate upload table for every category.

## 5. High-Level System Architecture

The proposed architecture consists of the following components:

  -----------------------------------------------------------------------
  Component                           Responsibility
  ----------------------------------- -----------------------------------
  React + TypeScript frontend         User interface for account
                                      management, profile editing,
                                      uploads, JD input, template
                                      selection, and resume review

  FastAPI backend                     Exposes application APIs and
                                      coordinates business logic

  PostgreSQL                          Stores users, profiles, structured
                                      professional information,
                                      documents, job descriptions,
                                      resumes, and related metadata

  Qdrant                              Stores vector embeddings and
                                      payloads for semantic retrieval

  RAG / orchestration layer           Coordinates document retrieval,
                                      context preparation, and AI
                                      generation

  Language model provider             Analyzes job requirements and
                                      generates resume content

  Document-processing tools           Extract text from uploaded files
                                      and prepare content for retrieval

  PDF-generation component            Renders the selected resume
                                      template into an exportable
                                      document
  -----------------------------------------------------------------------

The initial technology choices include: - **Frontend:** React and
TypeScript. - **Backend:** Python and FastAPI. - **Relational
database:** PostgreSQL. - **Vector database:** Qdrant. - **ORM and
migrations:** SQLAlchemy and Alembic. - **AI orchestration:** LangChain
and LangGraph. - **Model access:** A supported LLM API or a local model
through Ollama. - **Document processing:** Tools such as PyMuPDF and
python-docx. - **PDF generation:** HTML/CSS templates rendered to PDF,
for example with Playwright.

These are proposed technology choices; exact versions and provider
selections should be confirmed during implementation.

## 6. Database Overview

The database is designed for a multi-user application. Each user's
records must be associated with an owner and protected by authorization
checks.

### 6.1 Core Entities

  -----------------------------------------------------------------------
  Entity                              Purpose
  ----------------------------------- -----------------------------------
  `User`                              Stores account information such as
                                      username, email, and authentication
                                      data

  `Profile`                           Stores the user's personal and
                                      professional profile

  `Skill`                             Stores skills associated with a
                                      profile

  `WorkExperience`                    Stores employment history

  `Project`                           Stores personal, academic, or
                                      professional projects

  `Education`                         Stores educational background

  `Certification`                     Stores certificates and issuing
                                      information

  `Document`                          Stores metadata for every uploaded
                                      file, including its category and
                                      processing status

  `ExtractedData`                     Stores intermediate information
                                      extracted from source documents, if
                                      retained in the design

  `DocumentChunk`                     Stores chunk metadata and the
                                      corresponding Qdrant point
                                      identifier

  `JobDescription`                    Stores structured job information
                                      extracted from a JD document or
                                      entered manually

  `Resume`                            Stores a generated resume and its
                                      relationships to the user, JD, and
                                      template

  `ResumeTemplate`                    Stores available resume templates
                                      and their presentation data
  -----------------------------------------------------------------------

### 6.2 Main Relationships

The intended relationships include:

-   One user has one profile.
-   One user can upload many documents.
-   One profile can have many skills, work experiences, projects,
    education records, and certifications.
-   One document can produce many extracted-data records and document
    chunks.
-   One JD document can produce at most one structured job-description
    record in the initial design.
-   One user can manage many job descriptions and resumes.
-   One job description can be associated with many resumes.
-   One resume template can be used by many resumes.

Exact optionality, uniqueness, and foreign-key placement must be
finalized in the ERD before database migrations are created.

### Apply the local schema

From the repository root, set `POSTGRES_PASSWORD` in `infrastructure/.env`
using `infrastructure/.env.example` as a starting point. With Docker
Desktop running and the backend dependencies installed, run:

```powershell
docker compose -f infrastructure/docker-compose.yml up -d --wait postgres
.\.venv\Scripts\python.exe -m alembic upgrade head
.\.venv\Scripts\python.exe -m alembic current
```

Alembic uses the local Compose settings by default. Set `DATABASE_URL` in
the shell to use a different SQLAlchemy PostgreSQL connection URL.
The migrations create profiles first, then documents and review records,
then job descriptions, templates, and resumes.

A job description may link to one uploaded JD owned by the same user.
A resume may link to a job description owned by the same user and always
requires a template. Deleting the linked JD or source document clears the
optional reference. Deleting a document removes its chunk metadata and
extracted proposals. The upload service must clean up the original file
and Qdrant points separately.

Extracted data starts as a pending proposal. The application must review it
before applying changes to a profile and enforce ownership on reads and
writes. The chunk point ID stays empty until indexing. A completed resume
requires a stored content snapshot and generation time.

### 6.3 PostgreSQL and Qdrant Responsibilities

**PostgreSQL** stores authoritative structured data, including user
accounts, profile information, job descriptions, resume records,
document metadata, and relationships.

**Qdrant** stores vector embeddings and payloads used for semantic
search. PostgreSQL can store the corresponding Qdrant point IDs and
document-chunk metadata.

Vector embeddings should not be treated as ordinary relational
attributes. The embedding model and vector dimension should be selected
before creating the Qdrant collection.

## 7. Main Application Workflow

1.  **Registration:** A user creates an account and a profile.
2.  **Profile setup:** The user enters professional information manually
    or uploads personal documents.
3.  **Document processing:** The backend extracts text, creates chunks,
    generates embeddings, and stores retrieval data.
4.  **Profile validation:** Extracted information is reviewed and mapped
    to structured profile entities.
5.  **Job input:** The user uploads a JD document or enters a job
    description.
6.  **JD processing:** The system extracts and structures the job title,
    company, responsibilities, and requirements.
7.  **Evidence retrieval:** The RAG pipeline retrieves relevant profile
    information and supporting document chunks.
8.  **Resume generation:** The language model generates tailored content
    using the retrieved evidence and target JD.
9.  **Review:** The user checks and edits the generated resume.
10. **Export:** The system renders the resume using the selected
    template and provides an exportable document.

## 8. Data Integrity, Privacy, and Reliability

The system should follow these principles:

-   **User data isolation:** Every user-owned record must be protected
    by backend authorization and ownership checks.
-   **Truthful generation:** Generated resumes must not claim
    qualifications that are not supported by the user's profile or
    source documents.
-   **Source traceability:** Extracted information should be traceable
    to the document from which it originated.
-   **Validation before updates:** Document extraction should not
    silently overwrite existing profile data.
-   **Persistent storage:** Uploaded files and database records should
    use persistent storage appropriate to the deployment environment.
-   **Secret management:** Database passwords, API keys, and other
    secrets must be kept outside source control.
-   **Controlled migrations:** Database schema changes should be managed
    through Alembic migrations.
-   **Failure handling:** Document processing and resume generation
    should record errors and processing states so failed tasks can be
    retried or investigated.

## 9. Development Scope and Suggested Implementation Order

A practical implementation sequence is:

1.  Finalize the ERD, cardinalities, primary keys, foreign keys, and
    constraints.
2.  Set up PostgreSQL and Qdrant with Docker Compose.
3.  Configure FastAPI, SQLAlchemy, and Alembic.
4.  Implement authentication and user/profile CRUD operations.
5.  Implement structured profile entities.
6.  Implement document upload, storage, text extraction, and processing
    status.
7.  Implement chunking, embedding generation, and Qdrant retrieval.
8.  Implement job-description management and analysis.
9.  Implement RAG-based resume generation.
10. Implement resume templates, review, and PDF export.
11. Add version history, generation tracking, testing, and deployment
    improvements.

## 10. Project Summary

AI Resume Builder is a multi-user application that combines structured
professional-profile management with RAG-based document retrieval and
AI-assisted resume generation. Users provide their professional
information and a target job description; the system retrieves relevant
evidence, generates tailored resume content, and renders it through a
selected template.

The key architectural distinction is that PostgreSQL is the source of
truth for structured application data, while Qdrant supports semantic
retrieval over document content. This separation provides a foundation
for a maintainable system that can scale its document-processing and
resume-generation capabilities over time.
