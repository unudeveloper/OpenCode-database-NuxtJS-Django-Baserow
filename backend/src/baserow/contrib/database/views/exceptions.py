from baserow.core.exceptions import (
    InstanceTypeDoesNotExist, InstanceTypeAlreadyRegistered
)


class ViewDoesNotExist(Exception):
    """Raised when trying to get a view that doesn't exist."""


class UnrelatedFieldError(Exception):
    """
    Raised when a field is not related to the view. For example when someone tries to
    update field options of a field that does not belong to the view's table.
    """


class ViewTypeAlreadyRegistered(InstanceTypeAlreadyRegistered):
    pass


class ViewTypeDoesNotExist(InstanceTypeDoesNotExist):
    pass


class ViewFilterDoesNotExist(Exception):
    """Raised when trying to get a view filter that does not exist."""


class ViewFilterNotSupported(Exception):
    """Raised when the view type does not support filters."""


class ViewFilterTypeNotAllowedForField(Exception):
    """Raised when the view filter type is compatible with the field type."""


class ViewFilterTypeDoesNotExist(InstanceTypeDoesNotExist):
    """Raised when the view filter type was not found in the registry."""


class ViewFilterTypeAlreadyRegistered(InstanceTypeAlreadyRegistered):
    """Raised when the view filter type is already registered in the registry."""
