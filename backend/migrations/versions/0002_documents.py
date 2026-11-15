"""Create documents tables."""

from alembic import op

revision = "0002_documents"
down_revision = "0001_profiles"
branch_labels = None
depends_on = None


def upgrade():
    op.execute(
        """
        CREATE TABLE documents (
            id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
            user_id uuid NOT NULL REFERENCES users(id) ON DELETE CASCADE,
            category text NOT NULL CHECK (category IN ('personal', 'job_description')),
            file_name text NOT NULL,
            file_path text NOT NULL,
            uploaded_at timestamptz NOT NULL DEFAULT now(),
            processing_status text NOT NULL DEFAULT 'pending'
                CHECK (processing_status IN ('pending', 'processing', 'completed', 'failed')),
            processing_error text,
            UNIQUE (user_id, id, category)
        )
        """
    )
    op.execute(
        """
        CREATE TABLE document_chunks (
            id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
            document_id uuid NOT NULL REFERENCES documents(id) ON DELETE CASCADE,
            chunk_order integer NOT NULL CHECK (chunk_order >= 0),
            chunk_content text NOT NULL,
            qdrant_point_id uuid UNIQUE,
            UNIQUE (document_id, chunk_order),
            UNIQUE (document_id, id)
        )
        """
    )
    op.execute(
        """
        CREATE TABLE extracted_data (
            id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
            document_id uuid NOT NULL REFERENCES documents(id) ON DELETE CASCADE,
            source_chunk_id uuid,
            source_page integer CHECK (source_page > 0),
            data_type text NOT NULL,
            content jsonb NOT NULL,
            review_status text NOT NULL DEFAULT 'pending'
                CHECK (review_status IN ('pending', 'approved', 'rejected')),
            FOREIGN KEY (document_id, source_chunk_id)
                REFERENCES document_chunks(document_id, id) ON DELETE SET NULL (source_chunk_id)
        )
        """
    )
    op.execute("CREATE INDEX extracted_data_source_idx ON extracted_data (document_id, source_chunk_id)")


def downgrade():
    op.execute("DROP TABLE extracted_data")
    op.execute("DROP TABLE document_chunks")
    op.execute("DROP TABLE documents")
