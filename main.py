def run_lexer_repl():
    from lexer.repl import REPL
    repl = REPL()
    repl.run()


def run_parser_repl(mode: str):
    from parser.repl import REPL
    from parser.repl import Mode
    repl = REPL(Mode(mode))
    repl.run()


def run_evaluator_repl():
    from evaluator.repl import REPL
    repl = REPL()
    repl.run()


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("-r", "--run", default="eval")
    parser.add_argument("-m", "--mode", default="tostring")

    args = parser.parse_args()

    match args.run:
        case 'lexer':
            run_lexer_repl()
        case 'parser':
            run_parser_repl(args.mode)
        case 'eval':
            run_evaluator_repl()
        case _:
            print("unknown run type, will run as evaluator")
            run_evaluator_repl()
