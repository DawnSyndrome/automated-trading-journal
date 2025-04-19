from typing import Dict

### decorator functions
def with_preemptive_function(preemptive_func):
    def decorator(func):
        def wrapper(*args, **kwargs):
            updated_args = preemptive_func(*args, **kwargs)
            if isinstance(updated_args, tuple):
                args = updated_args
            elif updated_args is not None:
                args = (updated_args,)
            # call the original function
            return func(*args, **kwargs)
        return wrapper
    return decorator

### decorated functions
def get_matches_in_map(df, map_to_match: Dict, *args):
    df_colnames = df.columns.values.tolist()
    matched_map = {colname : custom_func for colname, custom_func in map_to_match.items() if colname in df_colnames}
    return df, matched_map, *args