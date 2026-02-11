"""Module containing classes related to setting a policy for how a knitting machine handles violations of the machine state's requirements."""

from __future__ import annotations

import warnings
from collections.abc import Callable, Generator
from contextlib import contextmanager
from dataclasses import dataclass, field
from functools import wraps
from typing import Any, Concatenate, ParamSpec, Protocol, TypeVar

from virtual_knitting_machine.knitting_machine_exceptions.Knitting_Machine_Exception import Knitting_Machine_Exception
from virtual_knitting_machine.knitting_machine_warnings.Knitting_Machine_Warning import Passed_Machine_Error_Warning
from virtual_knitting_machine.machine_state_violation_handling.machine_state_violations import (
    Violation,
    ViolationAction,
    ViolationResponse,
)


class Machine_State_With_Policy(Protocol):
    """Protocol for objects with policies for handling machine state errors."""

    @property
    def violation_policy(self) -> Knitting_Machine_Error_Policy:
        """
        Returns:
            Knitting_Machine_Error_Policy: The policy for handling machine state errors.
        """
        ...

    def set_response_for(self, violation: Violation, response: ViolationResponse | None = None) -> None:
        """
        Sets the response for the given violation to the given response.

        Args:
            violation (Violation): The violation to set the response for.
            response (ViolationResponse, optional): The response to set for the given violation. Defaults to the default response of this policy.
        """
        self.violation_policy.set_response_for(violation, response)

    @contextmanager
    def handle_violations(
        self,
        response_policy: ViolationResponse | Violation | None = None,
        handler: Callable[..., Any] | None = None,
    ) -> Generator[None, None, None]:
        """
        Context manager that catches exceptions and routes them through the violation policy.

        Args:
            response_policy (ViolationResponse | Violation, optional): The ViolationResponse policy for this code block.
                If given a Violation, the response will be the policy assigned to that violation in the violation policy.
                Defaults to the response will be the default response of the violation policy.
            handler (Callable[..., Any], optional): Optional handler to attempt before falling back to the policy response.
        """
        prior_policy_prevent_proceed = self.violation_policy.proceed
        try:
            yield
        except Exception as violation_exception:
            if response_policy is None:
                if isinstance(violation_exception, Knitting_Machine_Exception):
                    response: ViolationResponse = self.violation_policy.response_for(violation_exception.violation)
                else:
                    response: ViolationResponse = self.violation_policy.default
            elif isinstance(response_policy, Violation):
                response: ViolationResponse = self.violation_policy.response_for(response_policy)
            else:
                response: ViolationResponse = response_policy
            self.violation_policy.check_violation(response, violation_exception, handler)
            if not prior_policy_prevent_proceed:
                self.violation_policy.proceed = (
                    False  # Regardless of current result, stop procedure based on prior violations.
                )


P = ParamSpec("P")
R = TypeVar("R")


def checked_operation(method: Callable[Concatenate[Any, P], R]) -> Callable[Concatenate[Any, P], R]:
    """
    Decorator for methods that check machines tate violations against a Knitting_Machine_Error_Policy.
    The violation_policy will be set to proceed after completion of the wrapped method, regardless of code ignored based on violations of the policy.
    Args:
        method: A method of a Machine_State_With_Policy class that executes the operation being validated.

    Returns: The wrapped method.
    """

    @wraps(method)
    def wrapper(self: Machine_State_With_Policy, /, *args: P.args, **kwargs: P.kwargs) -> R:
        try:
            return method(self, *args, **kwargs)
        finally:
            self.violation_policy.proceed = True

    return wrapper


@dataclass
class Knitting_Machine_Error_Policy:
    """Controls how the virtual knitting machine responds to constraint violations."""

    _responses: dict[Violation, ViolationResponse] = field(
        default_factory=dict
    )  # Mapping of violation types to responses to those violations.
    default: ViolationResponse = field(
        default_factory=lambda: ViolationResponse(ViolationAction.RAISE, handle=False)
    )  # The default behavior for violations with no specific policy assigned.
    proceed: bool = True  # True if the policy allows the next operation to proceed. False otherwise.

    def set_response_for(self, violation: Violation, response: ViolationResponse | None = None) -> None:
        """
        Sets the response for the given violation to the given response.

        Args:
            violation (Violation): The violation to set the response for.
            response (ViolationResponse, optional): The response to set for the given violation. Defaults to the default response of this policy.
        """
        self._responses[violation] = response if response is not None else self.default

    def response_for(self, violation: Violation) -> ViolationResponse:
        """
        Args:
            violation (Violation): The violation type to get a response to.

        Returns:
            ViolationResponse: The response for the given violation.
        """
        return self._responses.get(violation, self.default)

    def check_violation(
        self,
        response: ViolationResponse,
        violation_exception: Exception,
        handler: Callable[..., Any] | None = None,
        **handler_kwargs: Any,
    ) -> None:
        """
        Check the given violation against this policy and act accordingly.
        Args:
            response (ViolationResponse): The response pattern to the violation.
            violation_exception (Exception): The exception to raised with the given violation.
            handler (Callable[[Machine_State_With_Policy], Any], optional):
                The handler for this specific check of a violation.
                The handler must take one positional argument that is a Machine_State_With_Policy handler and can have any return value that is ignored.
                Defaults to having no handler for the violation.
            handler_kwargs (Any): Optional keyword arguments to pass to the handler method. Note that self passed by default for methods of the calling class.

        Raises:
            Exception: The given violation exception if the policy for the violation is to raise the error.

        Warns:
            Passed_Machine_Error_Warning: A warning raised in place of the given exception if the violation's policy is to warn the user.
        """
        match response.action:
            case ViolationAction.RAISE:
                self.proceed = False  # Don't proceed because raising an exception
                raise violation_exception
            case ViolationAction.WARN:
                warnings.warn(Passed_Machine_Error_Warning(violation_exception, ignore_instructions=True), stacklevel=2)
        if handler is not None:
            handler(**handler_kwargs)
            self.proceed = True
        else:
            self.proceed = response.proceed_with_operation
