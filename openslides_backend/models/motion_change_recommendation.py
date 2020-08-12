from ..shared.patterns import Collection
from . import fields
from .base import Model


class MotionChangeRecommendation(Model):
    """
    Model for motion change_recommendation.
    """

    collection = Collection("motion_change_recommendation")
    verbose_name = "motion_change_recommendation"

    id = fields.IdField(description="The id of this motion change recommendation.")
    # Replacement (0), Insertion (1), Deletion (2), Other (3)
    type = fields.IntegerField(
        "The type of this motion change recommendation.", enum=[0, 1, 2, 3]
    )
    other_description = fields.CharField(
        "The other description of this motion change recommendation."
    )
    line_from = fields.PositiveIntegerField(
        "The line from of this motion change recommendation."
    )
    line_to = fields.PositiveIntegerField(
        "The line to of this motion change recommendation."
    )
    rejected = fields.BooleanField(
        description="If this motion change recommendation is rejected"
    )
    internal = fields.BooleanField(
        description="If this motion change recommendation is internal"
    )
    text = fields.TextField(description="The text of the motion change recommendation.")
    creation_time = fields.TimestampField(
        description="The creation_time of the motion change recommendation."
    )
    motion_id = fields.ForeignKeyField(
        description="The id of the motion of this motion change recommendation.",
        to=Collection("motion"),
        related_name="change_recommendation_ids",
    )
