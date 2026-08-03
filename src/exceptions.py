class ApplicationError(Exception):
    pass


class RoomNotFoundError(ApplicationError):
    pass


class ElementsNotFoundError(ApplicationError):
    pass


class AutobattleNotFoundError(ApplicationError):
    pass


class BattleResultNotFoundError(ApplicationError):
    pass


class TitanCountNotFoundError(ApplicationError):
    pass


