class ServiceHandlerResponse:
    """
    Wrapper class that encapsulates all the information the `call_apis`
    function needs to handle processing one service's output as another
    service's input. This class captures the return status of a service
    (status code), what data it sent back (its message content), and
    whether this data is fit for processing by another service (whether
    call_apis should continue). Some of the DIBBs services either do not
    return altered data to the caller, or return a 200 status code but
    still flag an error with their input, so capturing these nuances
    allows `call_apis` to be completely agnostic about the response
    content a service sends back.
    """

    def __init__(
        self, status_code: int, msg_content: str | dict, should_continue: bool
    ):
        self._status_code = status_code
        self._msg_content = msg_content
        self._should_continue = should_continue

    @property
    def status_code(self) -> int:
        """
        The status code the service returned to the caller.
        """
        return self._status_code

    @status_code.setter
    def status_code(self, code: int) -> None:
        """
        Decorator for setting status_code value as a property.
        :param code: The status code to set for a service's response.
        """
        self._status_code = code

    @property
    def msg_content(self) -> str | dict:
        """
        The data the service sent back to the caller. If this is a
        transformation or standardization service, this value holds
        the altered and updated data the service computed. If this
        is the validation or a verification service, this value
        holds any errors the service flagged in its input.
        """
        return self._msg_content

    @msg_content.setter
    def msg_content(self, content: str | dict) -> None:
        """
        Decorator for setting msg_content value as a property.
        :param content: The message content or error description to set
          as the returned value of a service's response.
        """
        self._msg_content = content

    @property
    def should_continue(self) -> bool:
        """
        Whether the calling function can hand the processed data off
        to the next service, based on the current service's status
        and message content validity.
        """
        return self._should_continue

    @should_continue.setter
    def should_continue(self, cont: bool) -> None:
        """
        Decorator for setting should_continue value as a property.
        :param cont: Whether the service's response merits continuing on
          to the next service.
        """
        self._should_continue = cont
