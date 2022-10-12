from hotkeys import *
from account import *
import threading

my_hotkey = Hotkeys()
my_account = Account()



def main():
    config=configparser.ConfigParser()
    config.read('cfg/config.ini')

    my_hotkey.hotkey = keyboard.HotKey(
            keyboard.HotKey.parse('<' + my_hotkey.first_hotkey + '>+<' + my_hotkey.second_hotkey + '>'),
            on_activate)

    my_hotkey.listener = keyboard.Listener(
            on_press=for_canonical(my_hotkey.hotkey.press),
            on_release=for_canonical(my_hotkey.hotkey.release))

    my_hotkey._start()
    my_hotkey._join()


def for_canonical(f):
    return lambda k: f(my_hotkey.listener.canonical(k))

def on_activate():
    print('Processing..')
    if (my_account.set_scaling_tp()):
        for order in my_account.orders:
            print('Selling ' + str(order[0]) + ' at $' + str(order[1]))
        print('Sold ' + str(len(my_account.orders)) + ' orders')
        my_account._clear_orders()
    else:
        print(my_account.debug)

if __name__ == '__main__':
    main()

