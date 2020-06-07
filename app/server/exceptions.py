class IdentificationTypeNotFoundException(Exception):
    """
    Raise if an identification type is supplied that does not exist in the application's identification type constants.
    """

    pass


class RoleNotFoundException(Exception):
    """
    Raise if provided role is not in organization's defined roles
    """

    pass
