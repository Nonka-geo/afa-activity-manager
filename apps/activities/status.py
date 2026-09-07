from enum import StrEnum


class ActivityStatus(StrEnum):
    AT_RISK = "At Risk"
    CONFIRMED = "Confirmed"
    FULL = "Full"
    WAITING_LIST = "Waiting List"


def calculate_status(registration_count, minimum_participants, maximum_participants):
    if registration_count < 0 or minimum_participants < 0 or maximum_participants < 0:
        raise ValueError("Registration counts and participant thresholds cannot be negative.")
    if minimum_participants > maximum_participants:
        raise ValueError("Minimum participants cannot exceed maximum participants.")
    if registration_count < minimum_participants:
        return ActivityStatus.AT_RISK
    if registration_count == maximum_participants:
        return ActivityStatus.FULL
    if registration_count > maximum_participants:
        return ActivityStatus.WAITING_LIST
    return ActivityStatus.CONFIRMED