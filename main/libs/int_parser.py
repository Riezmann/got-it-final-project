from main.commons.exceptions import ValidationError


def parse_positive_int(query_dict):
    data = {}
    for key, value in query_dict.items():
        int_value = int(value)
        if int_value <= 0:
            raise ValidationError(
                error_message="Query params must be positive integers"
            )
        data[key] = int(value)
    return data
