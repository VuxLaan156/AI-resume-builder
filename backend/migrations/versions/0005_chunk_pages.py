"""Preserve source page numbers on document chunks."""

import sqlalchemy as sa
from alembic import op

revision = "0005_chunk_pages"
down_revision = "0004_achievements"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column("document_chunks", sa.Column("page_number", sa.Integer()))
    op.create_check_constraint(
        "document_chunks_page_number_check", "document_chunks", "page_number > 0"
    )


def downgrade():
    op.drop_constraint("document_chunks_page_number_check", "document_chunks", type_="check")
    op.drop_column("document_chunks", "page_number")
