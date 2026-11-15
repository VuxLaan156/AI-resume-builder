"""Create profiles tables."""

from alembic import op

revision = "0001_profiles"
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.execute(
        """
        CREATE TABLE users (
            id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
            username text NOT NULL UNIQUE,
            email text NOT NULL,
            password_hash text,
            external_issuer text,
            external_subject text,
            UNIQUE (external_issuer, external_subject),
            CHECK ((external_issuer IS NULL) = (external_subject IS NULL)),
            CHECK (password_hash IS NOT NULL OR external_subject IS NOT NULL)
        )
        """
    )
    op.execute(
        """
        CREATE TABLE profiles (
            id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
            user_id uuid NOT NULL UNIQUE REFERENCES users(id) ON DELETE CASCADE,
            contact_info jsonb NOT NULL DEFAULT '{}',
            summary text
        )
        """
    )
    op.execute(
        """
        CREATE TABLE skills (
            id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
            profile_id uuid NOT NULL REFERENCES profiles(id) ON DELETE CASCADE,
            skill_name text NOT NULL,
            proficiency text,
            UNIQUE (profile_id, skill_name)
        )
        """
    )
    op.execute(
        """
        CREATE TABLE work_experiences (
            id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
            profile_id uuid NOT NULL REFERENCES profiles(id) ON DELETE CASCADE,
            job_title text NOT NULL,
            company_name text NOT NULL,
            description text,
            start_date date NOT NULL,
            end_date date,
            CHECK (end_date >= start_date)
        )
        """
    )
    op.execute(
        """
        CREATE TABLE projects (
            id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
            profile_id uuid NOT NULL REFERENCES profiles(id) ON DELETE CASCADE,
            project_name text NOT NULL,
            description text
        )
        """
    )
    op.execute(
        """
        CREATE TABLE education (
            id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
            profile_id uuid NOT NULL REFERENCES profiles(id) ON DELETE CASCADE,
            institution text NOT NULL,
            degree text NOT NULL,
            graduation_date date
        )
        """
    )
    op.execute(
        """
        CREATE TABLE certifications (
            id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
            profile_id uuid NOT NULL REFERENCES profiles(id) ON DELETE CASCADE,
            name text NOT NULL,
            issuing_body text NOT NULL,
            issue_date date
        )
        """
    )
    op.execute("CREATE UNIQUE INDEX users_email_ci ON users (lower(email))")
    op.execute("CREATE INDEX work_experiences_profile_id_idx ON work_experiences (profile_id)")
    op.execute("CREATE INDEX projects_profile_id_idx ON projects (profile_id)")
    op.execute("CREATE INDEX education_profile_id_idx ON education (profile_id)")
    op.execute("CREATE INDEX certifications_profile_id_idx ON certifications (profile_id)")


def downgrade():
    op.execute("DROP TABLE certifications")
    op.execute("DROP TABLE education")
    op.execute("DROP TABLE projects")
    op.execute("DROP TABLE work_experiences")
    op.execute("DROP TABLE skills")
    op.execute("DROP TABLE profiles")
    op.execute("DROP TABLE users")
