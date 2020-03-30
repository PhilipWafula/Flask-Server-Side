from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.ext.hybrid import hybrid_property
from typing import List
from typing import Optional

from app.server import db
from app.server.utils.enums.access_control_enums import AccessControlType
from app.server.utils.models import BaseModel
from app.server.utils.models import MutableList


class Configuration(BaseModel):
    """
    Creates system configuration table
    """
    __tablename__ = 'configurations'
    access_control_type = db.Column(db.Enum(AccessControlType))
    access_roles = db.Column(MutableList.as_mutable(ARRAY(db.String)))
    access_tiers = db.Column(MutableList.as_mutable(ARRAY(db.String)))
    domain = db.Column(db.String)

    organization_id = db.Column(db.Integer, db.ForeignKey('organizations.id'))
    organization = db.relationship('Organization', back_populates='configuration')

    @hybrid_property
    def roles(self):
        if self.access_roles is None:
            return []
        return self.access_roles

    @hybrid_property
    def tiers(self):
        if self.access_tiers is None:
            return []
        return self.access_tiers

    def set_access_attribute(self,
                             access_attribute_type: str,
                             roles_list: Optional[List] = None,
                             tiers_list: Optional[List] = None):

        if not access_attribute_type:
            raise ValueError('Access attribute type is missing')

        if access_attribute_type == 'role' and roles_list:
            for role in roles_list:
                if not isinstance(role, str):
                    raise ValueError('Role {} should be a string.'.format(role))
                role.upper()
                if role in self.roles:
                    raise ValueError('Duplicate role {} found. Cannot add to access roles'.format(role))
                self.access_roles.append(role)

        if access_attribute_type == 'tier' and tiers_list:
            for tier in tiers_list:
                if not isinstance(tier, str):
                    raise ValueError('Tier {} should be a string.'.format(tier))
                tier.upper()
                if tier in self.tiers:
                    raise ValueError('Duplicate tier {} found. Cannot add to access tiers'.format(tier))
                self.access_tiers.append(tier)

    def remove_specific_access_attribute(self,
                                         access_attribute_type: str,
                                         role: Optional[str] = None,
                                         tier: Optional[str] = None):

        if access_attribute_type == 'role' and role:
            if role not in self.access_roles:
                raise ValueError('Role {} not found in access roles.'.format(role))
            index = self.access_roles.index(role)
            self.access_roles.pop(index)

        if access_attribute_type == 'tier' and tier:
            if tier not in self.access_tiers:
                raise ValueError('Tier {} not found in access tiers.'.format(tier))
            index = self.access_tiers.index(tier)
            self.access_tiers.pop(index)

    def remove_all_access_attributes(self,
                                     access_attribute_type: str):

        if access_attribute_type == 'role':
            self.access_roles = []

        if access_attribute_type == 'tier':
            self.access_tiers = []

