import atexit
import code
import os
import readline
import rlcompleter


def interact(l):
    history_file = os.path.join(os.path.expanduser('~'), '.yellohist')
    console = code.InteractiveConsole(locals=l)
    readline.set_completer(rlcompleter.Completer(l).complete)
    try:
        readline.read_history_file(history_file)
    except IOError:
        pass
    readline.parse_and_bind("tab: complete")
    atexit.register(readline.write_history_file, history_file)
    console.interact()
