


def shell_escape(text):
    """
    Escape the passed text for use in the shell (Bash).
    The output text will be enclosed in double quotes.
    """
    if not text:
        return '""'
    # We need to escape special characters for bash, and in
    # Python, two backslashes represent one literal backslash.
    # Escape backslashes first, otherwise you would end up escaping the
    # other special characters' escape backslash.
    text = text.replace("\\", "\\\\")
    text = text.replace("$", "\\$")
    text = text.replace("`", "\\`")
    text = text.replace('"', '\\"')
    return '"%s"' % text
