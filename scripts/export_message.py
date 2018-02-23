#!/usr/bin/env python3


# import modules.
import os
import plac
import sys
from lxml import etree


def export_message(eaxs, output_file, message_id):
    """ Exports a <Message> element from a given EAXS or tagged EAXS file and writes the 
    content to @output_file.

    Args:
        - eaxs (str): The EAXS file from which to extract a <Message> element.
        - output_file (str): The file in which to write the extracted message.
        - message_id (str OR int): The <MessageId> value OR the position of the message (1 =
        the first message in @eaxs).

    Returns:
        bool: The return value.
        True if the message was found. Otherwise, False.

    Raises:
        FileExistsError: If @output_file already exists.
    """

    if os.path.isfile(output_file):
        msg = "File '{}' already exists.".format(output_file)
        raise FileExistsError(msg)

    # loop through @eaxs_file and:
    #   1. find the <Message> with the given @message_id,
    #   2. print the <Message> element to @output_file.
    i = 1
    is_found = False
    for event, element in etree.iterparse(eaxs, huge_tree=True, strip_cdata=False):
        if element.tag == "{http://www.archives.ncdcr.gov/mail-account}MessageId":
            if element.text == message_id or str(i) == message_id:
                is_found = True
                message = element.getparent()
                with open(output_file, "w", encoding="utf-8") as xf:
                    xf.write(etree.tostring(message).decode(encoding="utf-8"))
                    break
            i += 1
        element.clear()

    return is_found


def main(eaxs:"any EAXS file", 
        output_file:"output file", 
        message_id:"<MessageID> value or message position"):
    
    "Exports a single <Message> element from an EAXS or tagged EAXS file.\
    \nexample: `py -3 export_message.py myEAXS.xml myEAXS__message_123abc.xml \"<123abc>\"`\
    \nexample: `py -3 export_message.py myEAXS.xml myEAXS__firstMessage.xml 1` "

    try:
        results = export_message(eaxs, output_file, message_id)
        if not results:
            print("Message not found.")
        else:
            print("Found message.")
        sys.exit()
    except Exception as err:
        sys.exit(err)


if __name__ == "__main__":
    plac.call(main)
