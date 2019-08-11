def convert(model):
    if isinstance(model, list):
        result = []
        for obj in model:
            result.append(convert(obj))
        return result

    dict_row = model.__dict__
    result = {}

    for key, value in dict_row.items():
        if value is None:
            continue
        elif key in ['spots']:
            new_value = []
            for val in value:
                new_value.append(convert(val))
            result[key] = new_value
        elif key in ['reservation']:
            result[key] = convert(value)
        elif key not in ['_sa_instance_state']:
            result[key] = value

    return result