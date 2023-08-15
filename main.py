from cmd import Cmd
from parser import Parser

QUIT_COMMAND = 'quit'


class CommandInterpreter(Cmd):
    prompt = 'cmd> '
    intro = ''

    def __init__(self, p: Parser):
        super().__init__()
        self.parser = p

    # trap EOF (CTRL-D)
    def do_EOF(self, _) -> bool:
        self.parser.quit()
        return True

    # ignore empty lines
    def emptyline(self) -> bool:
        return False

    def do_help(self, topic: str):
        pass

    # Process command
    def default(self, command: str):
        self.parser.execute(command)

    def do_bye(self, _: str) -> bool:
        self.parser.execute(QUIT_COMMAND)
        return True


if __name__ == '__main__':
    parser = Parser()
    ci = CommandInterpreter(parser)
    try:
        ci.cmdloop()
    except KeyboardInterrupt:
        parser.quit()
