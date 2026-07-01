class DashboardError(Exception):
    """Base exception for expected dashboard errors."""


class DataValidationError(DashboardError):
    """Raised when a dataset does not satisfy the expected schema."""


class DataSourceError(DashboardError):
    """Raised when a data source cannot be read."""


class ForecastError(DashboardError):
    """Raised when there is not enough data for a forecast."""
