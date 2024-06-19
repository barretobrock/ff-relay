
def default_if_prop_none(obj, prop_name: str, default: str = '') -> str:
    """Simple one-liner for logic if empty object property shouldn't be empty for form"""
    if '.' in prop_name:
        prop_name_split = prop_name.split('.', maxsplit=1)
        sub_obj = getattr(obj, prop_name_split[0])
        if sub_obj is None:
            return default
        else:
            return default_if_prop_none(sub_obj, prop_name_split[1])
    return default if getattr(obj, prop_name) is None else getattr(obj, prop_name)
