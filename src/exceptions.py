class StopApplicationError(Exception):
    """Ошибка приложения, которая приводит к остановке выполнения."""


class RetryApplicationError(Exception):
    """Ошибка приложения, которая приводит к повторной попытке выполнения."""


class ApplicationError(StopApplicationError):
    pass


################## DEPRECATED ERRORS ###################
class RoomNotFoundError(StopApplicationError):
    pass


class ElementsNotFoundError(StopApplicationError):
    pass


class AutobattleNotFoundError(StopApplicationError):
    pass


class BattleResultNotFoundError(StopApplicationError):
    pass


class TitanCountNotFoundError(RetryApplicationError):
    pass


class TitanNotIdentifiedError(RetryApplicationError):
    pass


########################################################
