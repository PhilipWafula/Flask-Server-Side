from app.server.models.user import User
from app.server.exceptions import RoleNotFoundException
from app.server.exceptions import TierNotFoundException
from app.server.utils.enums.access_control_enums import AccessControlType


def _user_tier_matches_required_tier(user_tier: str, required_tier: str, tier_list: list):
    if user_tier is None:
        return False

    # check that user's tier is in organization tiers
    if user_tier not in tier_list:
        raise TierNotFoundException('User tier {} not recognized.'.format(user_tier))

    # that required role is in organization tiers
    if required_tier not in tier_list:
        raise TierNotFoundException('Required tier {} not recognized.'.format(required_tier))

    # check if tiers are matching
    are_matching_tiers = tier_list.index(user_tier) == tier_list.index(required_tier)

    return are_matching_tiers


class AccessControl:
    """
    This module defines methods to manage access depending on the a user's parent organization's access control
    configuration.
    """

    def __init__(self, user: User):
        # get user's parent organization
        self.organization = user.parent_organization

        # get organization's configuration
        self.organization_configuration = self.organization.configuration

        # get access control type
        self.access_control_type = self.organization_configuration.access_control_type

    # check if organization has standard access control type
    def has_standard_access_control_type(self):
        return self.access_control_type == AccessControlType.STANDARD_ACCESS_CONTROL

    # check if organization has tiered access control type
    def has_tiered_access_control_type(self):
        return self.access_control_type == AccessControlType.TIERED_ACCESS_CONTROL

    def has_required_role(self, user_role_dict: dict, required_role_dict: dict) -> bool:
        # define organization roles
        organization_roles = self.organization_configuration.access_roles

        try:
            for (role, tier) in required_role_dict.items():
                # check that role is in organization's roles
                if role not in organization_roles:
                    raise RoleNotFoundException('Role {} not recognized for organization {}.'
                                                .format(role, self.organization.name))
                # handle standard access control
                if self.has_standard_access_control_type():
                    return user_role_dict[role] == 'STANDARD'

                # handle tiered access control
                if self.has_tiered_access_control_type():
                    return role in organization_roles

            return False
        except Exception as exception:
            raise Exception('An error occurred: {}'.format(exception))

    def has_required_tier(self, user_role_dict: dict, required_tier: str) -> bool:
        # define organization tiers
        organization_tiers = self.organization_configuration.access_tiers

        try:
            for (role, tier) in user_role_dict.items():
                # check if tier in organization tiers
                if required_tier not in organization_tiers:
                    raise TierNotFoundException('Required tier {} not recognised for role {} in organization {}.'
                                                .format(required_tier,
                                                        role,
                                                        self.organization.name))

                # check if required tier is any
                if required_tier == 'any':
                    return True

                # check if user has sufficient clearance
                is_sufficient_clearance = _user_tier_matches_required_tier(tier,
                                                                           required_tier,
                                                                           organization_tiers)
                return is_sufficient_clearance

            return False
        except Exception as exception:
            raise Exception('An error occurred: {}'.format(exception))
