from main.commons.exceptions import ValidationError


def parse_int(*list_of_strings):
    try:
        return [int(string) for string in list_of_strings]
    except ValueError:
        raise ValidationError(
            error_message="Query params are not integers",
        )
