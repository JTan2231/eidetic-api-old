# TODO: docstring
def extract_text_from_html(html):
    output_text = ""

    i = 0
    while i < len(html):
        if html[i] == '<':
            while html[i] != '>':
                i += 1

            output_text += " "
        else:
            output_text += html[i]

        i += 1

    return output_text
