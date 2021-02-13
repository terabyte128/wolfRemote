import threading


def run(fns, args):
    for f, a in zip(fns, args):
        t = threading.Thread(target=f, args=a)
        t.start()
