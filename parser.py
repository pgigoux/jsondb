from lexer import Lexer


if __name__ == '__main__':
    lx = Lexer()
    while True:
        try:
            command = input('db> ')
            lx.input(command)
            for t in lx.next():
                print(t)
        except (KeyboardInterrupt, EOFError):
            break
