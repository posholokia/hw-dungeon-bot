from threading import Event

from structlog import get_logger

from exceptions import RetryApplicationError, StopApplicationError
from models.dto import State
from use_cases.select_room import SelectRoomUseCase

logger = get_logger(__name__)


class BotRunner:
    def __init__(
        self,
        select_room_use_case: SelectRoomUseCase,
    ) -> None:
        self._select_room = select_room_use_case

    def run(self, stop_event: Event) -> None:
        logger.info("Bot started2")
        state = State()
        logger.info(f"State:{state}")
        logger.info(f"Stop event:{stop_event.is_set()}")
        while not stop_event.is_set():
            logger.info("Running select room use case")
            try:
                logger.info("Executing select room use case")
                self._select_room.execute(state, stop_event)
            except StopApplicationError as e:
                logger.info(e.__str__())
                return
            except RetryApplicationError as e:
                logger.info(e.__str__())
                continue
            except Exception as e:
                logger.exception(e.__str__())
                return
        logger.info("Bot stopped")
