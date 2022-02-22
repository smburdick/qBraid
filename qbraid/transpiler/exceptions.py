"""Exceptions for errors raised while handling circuits."""

from qbraid.exceptions import QbraidError


class TranspilerError(QbraidError):
    """Base class for errors raised while transpiling a circuit."""


class CircuitConversionError(TranspilerError):
    pass
