from flask import render_template


def convert(model_obj):
    if isinstance(model_obj, list):
        result = []
        for obj in model_obj:
            result.append(convert(obj))
        return result

    dict_row = model_obj.__dict__
    result = {}

    for key, value in dict_row.items():
        if value is None:
            continue
        elif key in ['spots']:
            new_value = []
            for val in value:
                new_value.append(convert(val))
            result[key] = new_value
        elif key in ['reservation', 'spot']:
            result[key] = convert(value)
        elif key not in ['_sa_instance_state']:
            result[key] = value

    return result


def delay(route: str, flags: list):
    def invoke(new_flags: list, data=None, js=None):
        args = {} if data is None else {'data': data}
        if js is not None:
            args['js'] = js
        for flag in flags + new_flags:
            args[flag] = True
        return render_template(route, **args)

    return invoke
