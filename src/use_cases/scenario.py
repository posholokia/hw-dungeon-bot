# """DEPRECATED"""

# import logging
# from threading import Event

# from exceptions import ApplicationError, StopApplicationError
# from interfaces.flow import IStep
# from models.dto import State

# logger = logging.getLogger(__name__)


# class Scenario:
#     def __init__(
#         self,
#         steps: list[IStep],
#     ) -> None:
#         self._steps = steps

#     def run(self, state: State, stop_event: Event) -> None:
#         while not stop_event.is_set():
#             try:
#                 for step in self._steps:
#                     if stop_event.is_set():
#                         return
#                     step.execute(state, stop_event)
#                     if stop_event.is_set():
#                         return
#             except StopApplicationError as e:
#                 logger.info("StopApplicationError: %s", e)
#                 return
#             except ApplicationError as e:
#                 logger.error("ApplicationError: %s", e)

#         logger.info("Stopped")
