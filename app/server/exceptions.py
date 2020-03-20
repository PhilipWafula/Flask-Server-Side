class IdentificationTypeNotFound(Exception):
    """
    Raise if an identification type is supplied that does not exist in the application's identification type constants.
    """
    pass


class RoleNotFound(Exception):
    """
    Raise if provided role is not in organization's defined roles
    """
    pass


class TierNotFound(Exception):
    """
    Raise if provided tier is not in organization's defined tier
    """
    pass
