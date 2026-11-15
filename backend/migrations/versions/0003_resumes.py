"""Create resumes tables."""

from alembic import op

revision = "0003_resumes"
down_revision = "0002_documents"
branch_labels = None
depends_on = None


def upgrade():
    op.execute(
        """
        CREATE TABLE job_descriptions (
            id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
            user_id uuid NOT NULL REFERENCES users(id) ON DELETE CASCADE,
            source_document_id uuid UNIQUE,
            source_category text NOT NULL DEFAULT 'job_description'
                CHECK (source_category = 'job_description'),
            title text NOT NULL,
            company_name text,
            description text NOT NULL,
            requirements text,
            UNIQUE (user_id, id),
            FOREIGN KEY (user_id, source_document_id, source_category)
                REFERENCES documents(user_id, id, category) ON DELETE SET NULL (source_document_id)
        )
        """
    )
    op.execute(
        """
        CREATE TABLE resume_templates (
            id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
            template_name text NOT NULL UNIQUE,
            template_data jsonb NOT NULL
        )
        """
    )
    op.execute(
        """
        CREATE TABLE resumes (
            id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
            user_id uuid NOT NULL REFERENCES users(id) ON DELETE CASCADE,
            job_id uuid,
            template_id uuid NOT NULL REFERENCES resume_templates(id) ON DELETE RESTRICT,
            generated_content jsonb,
            generated_at timestamptz,
            generation_status text NOT NULL DEFAULT 'pending'
                CHECK (generation_status IN ('pending', 'processing', 'completed', 'failed')),
            generation_error text,
            created_at timestamptz NOT NULL DEFAULT now(),
            CHECK (generation_status <> 'completed'
                OR (generated_content IS NOT NULL AND generated_at IS NOT NULL)),
            FOREIGN KEY (user_id, job_id)
                REFERENCES job_descriptions(user_id, id) ON DELETE SET NULL (job_id)
        )
        """
    )
    op.execute("CREATE INDEX resumes_owner_job_idx ON resumes (user_id, job_id)")
    op.execute("CREATE INDEX resumes_template_idx ON resumes (template_id)")


def downgrade():
    op.execute("DROP TABLE resumes")
    op.execute("DROP TABLE resume_templates")
    op.execute("DROP TABLE job_descriptions")
