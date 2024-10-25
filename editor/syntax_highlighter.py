from abc import ABC, abstractmethod
from pygments import lex
from pygments.lexers import get_lexer_by_name, guess_lexer
from pygments.token import Token

class SyntaxHighlighter(ABC):
    @abstractmethod
    def highlight(self, lines):
        pass

class PygmentsSyntaxHighlighter(SyntaxHighlighter):
    def __init__(self, language_name=None):
        if language_name:
            try:
                self.lexer = get_lexer_by_name(language_name)
            except Exception:
                self.lexer = None
        else:
            self.lexer = None

    def highlight(self, lines):
        text = '\n'.join(lines)
        if self.lexer:
            tokens = lex(text, self.lexer)
        else:
            # Guess the lexer if not specified
            try:
                self.lexer = guess_lexer(text)
                tokens = lex(text, self.lexer)
            except Exception:
                # Default to no highlighting
                return [[] for _ in lines]

        highlighted_lines = [[] for _ in lines]
        current_line = 0
        current_pos = 0

        for tok_type, tok_value in tokens:
            tok_lines = tok_value.split('\n')
            for i, tok_line in enumerate(tok_lines):
                if i > 0:
                    current_line += 1
                    current_pos = 0

                if current_line >= len(lines):
                    break

                length = len(tok_line)
                if length == 0:
                    continue

                format_name = self.token_to_format_name(tok_type)

                highlighted_lines[current_line].append((current_pos, length, format_name))
                current_pos += length

        return highlighted_lines

    def token_to_format_name(self, token_type):
        """
        Map Pygments token types to format names.
        """
        if token_type in Token.Text:
            return 'text'
        elif token_type in Token.Keyword:
            if token_type in Token.Keyword.Declaration:
                return 'keyword_declaration'
            elif token_type in Token.Keyword.Namespace:
                return 'keyword_namespace'
            elif token_type in Token.Keyword.Pseudo:
                return 'keyword_pseudo'
            elif token_type in Token.Keyword.Reserved:
                return 'keyword_reserved'
            elif token_type in Token.Keyword.Type:
                return 'keyword_type'
            else:
                return 'keyword'
        elif token_type in Token.Name:
            if token_type in Token.Name.Builtin:
                return 'name_builtin'
            elif token_type in Token.Name.Function:
                return 'name_function'
            elif token_type in Token.Name.Class:
                return 'name_class'
            elif token_type in Token.Name.Decorator:
                return 'name_decorator'
            elif token_type in Token.Name.Exception:
                return 'name_exception'
            elif token_type in Token.Name.Variable:
                return 'name_variable'
            elif token_type in Token.Name.Constant:
                return 'name_constant'
            elif token_type in Token.Name.Attribute:
                return 'name_attribute'
            else:
                return 'name'
        elif token_type in Token.Literal:
            if token_type in Token.Literal.String:
                if token_type in Token.Literal.String.Doc:
                    return 'string_doc'
                elif token_type in Token.Literal.String.Interpol:
                    return 'string_interpol'
                elif token_type in Token.Literal.String.Escape:
                    return 'string_escape'
                else:
                    return 'string'
            elif token_type in Token.Literal.Number:
                return 'number'
            else:
                return 'literal'
        elif token_type in Token.Operator:
            return 'operator'
        elif token_type in Token.Punctuation:
            return 'punctuation'
        elif token_type in Token.Comment:
            if token_type in Token.Comment.Multiline:
                return 'comment_multiline'
            elif token_type in Token.Comment.Preproc:
                return 'comment_preproc'
            else:
                return 'comment'
        elif token_type in Token.Generic:
            if token_type in Token.Generic.Deleted:
                return 'generic_deleted'
            elif token_type in Token.Generic.Emph:
                return 'generic_emph'
            elif token_type in Token.Generic.Error:
                return 'generic_error'
            elif token_type in Token.Generic.Heading:
                return 'generic_heading'
            elif token_type in Token.Generic.Inserted:
                return 'generic_inserted'
            elif token_type in Token.Generic.Output:
                return 'generic_output'
            elif token_type in Token.Generic.Prompt:
                return 'generic_prompt'
            elif token_type in Token.Generic.Strong:
                return 'generic_strong'
            elif token_type in Token.Generic.Subheading:
                return 'generic_subheading'
            elif token_type in Token.Generic.Traceback:
                return 'generic_traceback'
            else:
                return 'generic'
        elif token_type in Token.Error:
            return 'error'
        else:
            return 'text'  # Default format
