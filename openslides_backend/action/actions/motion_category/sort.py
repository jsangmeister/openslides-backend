from ....models.models import MotionCategory
from ...generics.update import UpdateAction
from ...mixins.singular_action_mixin import SingularActionMixin
from ...mixins.tree_sort_mixin import TreeSortMixin
from ...util.default_schema import DefaultSchema
from ...util.register import register_action
from ...util.typing import ActionPayload


@register_action("motion_category.sort")
class MotionCategorySort(TreeSortMixin, SingularActionMixin, UpdateAction):
    """
    Action to sort motion categories.
    """

    model = MotionCategory()
    schema = DefaultSchema(MotionCategory()).get_tree_sort_schema()
    permission_description = "motion.can_manage"

    def get_updated_instances(self, payload: ActionPayload) -> ActionPayload:
        payload = super().get_updated_instances(payload)
        # Payload is an iterable with exactly one item
        instance = next(iter(payload))
        yield from self.sort_tree(
            nodes=instance["tree"],
            meeting_id=instance["meeting_id"],
            weight_key="weight",
            parent_id_key="parent_id",
            children_ids_key="child_ids",
            set_level=True,
        )
