from warlock_manager.config.base_config import BaseConfig


def cli_formatter(
    data: BaseConfig,
    section: str = 'flag',
    prefix: str = '-',
    sep: str = ' ',
    joiner: str = ' ',
    true_value: str | bool = 'True',
    false_value: str | bool = 'False',
) -> str:
    """
    Format a given Configuration object as CLI arguments.

    ## True/False Formatting

    The most complicated part of this is handling true/false boolean values.

    The default is to render bool TRUE values as -key_name=True and bool FALSE values as -key_name=False

    Render bool TRUE values as -key_name and bool FALSE values are omitted completely

    ```python
    cli_formatter(..., prefix='-', true_value=True, false_value=False)
    ```

    The inverse is possible too, to omit TRUE values and only render FALSE values.

    ```python
    cli_formatter(..., prefix='-', true_value=False, false_value=True)
    ```

    Render bool TRUE values as -key_name=true and bool FALSE values as -key_name=false

    ```python
    cli_formatter(..., prefix='-', true_value='true', false_value='false')
    ```

    Render bool TRUE values as ?key_name:YUP and bool FALSE values as ?key_name:LULZNOPE

    ```python
    cli_formatter(..., prefix='?', sep=':', true_value='YUP', false_value='LULZNOPE')
    ```

    :param data:
    :param section:
    :param prefix:
    :param sep:
    :param joiner:
    :param true_value:
    :param false_value:
    :return:
    """
    values = []
    for opt in data.options.values():
        if opt.section != section:
            # Only parse options which belong to the requested section.
            continue

        if not data.has_value(opt.name):
            # Only include options that have a value set.
            # This value can be True, False, a number, string, etc.
            # It just needs to be _something_.
            continue

        value = data.get_value(opt.name)

        if opt.val_type == 'bool' and value is True:
            # Booleans are special; they can be present with the string values
            # OR just present / absent in general.
            if true_value is True:
                values.append('%s%s' % (prefix, opt.key))
            elif true_value is not False:
                values.append('%s%s%s%s' % (prefix, opt.key, sep, true_value))
        elif opt.val_type == 'bool' and value is False:
            # Booleans are special; they can be present with the string values
            # OR just present / absent in general.
            if false_value is True:
                values.append('%s%s' % (prefix, opt.key))
            elif false_value is not False:
                values.append('%s%s%s%s' % (prefix, opt.key, sep, false_value))
        elif opt.val_type == 'int' or opt.val_type == 'float':
            values.append('%s%s%s%s' % (prefix, opt.key, sep, str(value)))
        else:
            if '"' in value:
                value = "'%s'" % value
            elif "'" in value or ' ' in value or '?' in value or '=' in value or '-' in value:
                value = '"%s"' % value
            values.append('%s%s%s%s' % (prefix, opt.key, sep, value))

    return joiner.join(values)
