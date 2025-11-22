"""empty message

Revision ID: b84bd9102a2d
Revises: 1fc51cc70b43
Create Date: 2025-11-21 23:40:12.943403

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'b84bd9102a2d'
down_revision = '1fc51cc70b43'
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table("friendships", schema=None) as batch_op:
        # add the column (nullable so existing rows are ok)
        batch_op.add_column(sa.Column("initiator_id", sa.Integer(), nullable=True))

        # explicitly named foreign key constraint
        batch_op.create_foreign_key(
            "fk_friendships_initiator_id_users",
            "users",              # referent table
            ["initiator_id"],     # local cols
            ["id"],               # remote cols
            ondelete="CASCADE",
        )


def downgrade():
    with op.batch_alter_table("friendships", schema=None) as batch_op:
        # drop the FK first, using the same name
        batch_op.drop_constraint(
            "fk_friendships_initiator_id_users",
            type_="foreignkey",
        )
        # then drop the column
        batch_op.drop_column("initiator_id")

    # ### end Alembic commands ###
