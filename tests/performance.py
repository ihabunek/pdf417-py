"""
A simple performance test.
"""

from datetime import datetime
from pdf417gen import encode, render_image

ZEN = """
Beautiful is better than ugly.
Explicit is better than implicit.
Simple is better than complex.
Complex is better than complicated.
Flat is better than nested.
Sparse is better than dense.
Readability counts.
Special cases aren't special enough to break the rules.
Although practicality beats purity.
Errors should never pass silently.
Unless explicitly silenced.
In the face of ambiguity, refuse the temptation to guess.
There should be one-- and preferably only one --obvious way to do it.
Although that way may not be obvious at first unless you're Dutch.
Now is better than never.
Although never is often better than *right* now.
If the implementation is hard to explain, it's a bad idea.
If the implementation is easy to explain, it may be a good idea.
Namespaces are one honking great idea -- let's do more of those!
""".strip()


def test_encode(cycles=1000):
    start = datetime.now()
    for _ in range(cycles):
        encode(ZEN)
    duration = datetime.now() - start
    print("Encode x{}: {}".format(cycles, duration))


def test_render_image(cycles=1000):
    codes = encode(ZEN)
    start = datetime.now()
    for _ in range(cycles):
        render_image(codes)
    duration = datetime.now() - start
    print("Render x{}: {}".format(cycles, duration))


if __name__ == "__main__":
    test_encode()
    test_render_image()
