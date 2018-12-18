# Tagged EAXS: message example

Consider this basic example message within an EAXS file:

> TOMES is a multi-state partnership that includes Kansas <http://www.kshs.or=
g/, Utah <http://archives.utah.gov/ and North Carolina <http://archives=
.ncdcr.gov/ ...

This message would be found within the `/Account/Folder/Message/MultiBody/SingleBody/BodyContent/Content` EAXS XML element.

## Tagged EAXS elements
Tagged EAXS files contain two additional message-related XML elements:

1. `/Account/Message/MultiBody/SingleBody/TaggedContent`
2. `/Account/Message/MultiBody/SingleBody/StrippedContent`

### TaggedContent element
The `TaggedContent` element's value would contain a semantic version of the message as follows:

    <Tokens xmlns="https://github.com/StateArchivesOfNorthCarolina/tomes-eaxs"><Token>TOMES</Token> <Token>is</Token> <Token>a</Token> <Token>multi-state</Token> <Token>partnership</Token> <Token>that</Token> <Token>includes</Token> <Token>Kansas</Token> <Token>&lt;</Token><Token entity="TOMES.URL" group="1" pattern="2aa1a6#0001" authority="nc.gov">http://www.kshs.org/</Token><Token>&gt;</Token> <Token>,</Token> <Token entity="LOCATION" group="2" authority="stanford.edu">Utah</Token> <Token>&lt;</Token><Token entity="TOMES.URL" group="3" pattern="2aa1a6#0001" authority="nc.gov">http://archives.utah.gov/</Token><Token>&gt;</Token>  <Token>and</Token> <Token entity="LOCATION" group="4" authority="stanford.edu">North</Token> <Token entity="LOCATION" group="4" authority="stanford.edu">Carolina</Token> <Token>&lt;</Token><Token entity="TOMES.URL" group="5" pattern="2aa1a6#0001" authority="nc.gov">http://archives.ncdcr.gov/</Token><Token>&gt;</Token>  <Token>...</Token></Tokens>

Note that whitespace within the original message is considered significant. Therefore, the semantic version of the message is not pretty-printed within the tagged EAXS file.

*For more information on the schema for the semantic message contained within the `TaggedContent` element, see the `./tomes_tagger/lib/nlp_to_xml.xsd` XML schema file.*

### StrippedContent element
The `StrippedContent` element is simply a plain-text version of the message found within the tagged EAXS file **if** the message was originally in HTML format.

If the original message was in HTML format, it is this "stripped" version of the original message that is subjected to Named Entity Recognition. Otherwise, entities are found within the original, plain-text message.
