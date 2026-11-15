"""Create standalone profile achievements."""

from alembic import op

revision = "0004_achievements"
down_revision = "0003_resumes"
branch_labels = None
depends_on = None


def upgrade():
    op.execute(
        """
        CREATE TABLE achievements (
            id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
            profile_id uuid NOT NULL REFERENCES profiles(id) ON DELETE CASCADE,
            title text NOT NULL,
            description text,
            achievement_date date
        )
        """
    )
    op.create_index("achievements_profile_id_idx", "achievements", ["profile_id"])


def downgrade():
    op.drop_table("achievements")
