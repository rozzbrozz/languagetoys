"""
A simpler/cleaner verse generator than verse.py.
First get cmudict.0.7a from http://www.speech.cs.cmu.edu/cgi-bin/cmudict
and put it in this directory.
Then run
   $ python simpleverse.py 14
in a terminal.
"""

import itertools
import random
import sys

if __name__ == '__main__':
    import ansi
else:
    class ansi:
        home = ''
        clear_to_eol = ''
        clear_to_bottom = ''

def main(argv):
    show(versify(int(argv[1])))
    print redisplay_count()
    return 0

def show(lines, out=sys.stdout):
    "Display a verse. We try to avoid flicker in redisplay."
    out.write(ansi.home)
    for line in lines:
        out.write(' '.join(line) + ansi.clear_to_eol + '\n')
        if False: print '  ', ' '.join('-'.join(pronunciations[word])
                                       for word in line)
    out.write(ansi.clear_to_bottom)

def redisplay(lines):
    if redisplay_count() % 1000 == 0:
        show(lines)

redisplay_count = itertools.count().next

def versify(nlines):
    "Compose nlines lines of verse."
    lines = [[]]
    while True:
        redisplay(lines)
        append_word(lines)
        value = evaluate(lines[-1], lines)
        if value == 'good':
            if len(lines) == nlines:
                break
            lines.append([])
        elif value == 'bad':
            backtrack(lines)
    return lines

def append_word(lines):
    lines[-1].append(random.choice(vocabulary))

def backtrack(lines):
    distance = int(1 + random.expovariate(2.5))
    for i in range(distance):
        while not lines[-1]:
            if len(lines) == 1: return
            lines.pop()
        lines[-1].pop()

def evaluate(line, lines):
    "Return an evaluation of the last line: bad, incomplete, or good."
    phones = pronounce(line)
    if not is_iambic(phones):
        return 'bad'
    nsyllables = sum(map(is_vowel, phones))
    if 10 < nsyllables:
        return 'bad'            # TODO: allow 'feminine' endings
    elif nsyllables < 10:
        return 'incomplete'
    else:
        return 'good' if rhymes_ok(phones, lines) else 'bad'

def is_iambic(phones):
    "We deem phones iambic if the odd-numbered syllables are unstressed."
    rhythm = [phone[-1] for phone in phones if phone[-1] in '012']
    return all(i % 2 == 1 or stress == '0' for i, stress in enumerate(rhythm))

def is_vowel(phone):
    return phone[-1] in '012'


# Shakespearean-sonnet rhyme scheme
rhyme_lines = [[],[], [0],[1],[],[],[4],[5],[],[],[8],[9],[],    [12]]
anti_lines  = [[],[0],[], [], [],[4],[],[], [],[8],[],[],  [8,9],[]]

def rhymes_ok(phones, lines):
    "Does phones, as the last line, fit the rhyme scheme?"
    n = len(lines) - 1
    return (all(rhymes(phones, pronounce(lines[j]))
                for j in rhyme_lines[n])
            and not any(rhymes(phones, pronounce(lines[j]))
                        for j in anti_lines[n]))

def rhymes(phones1, phones2):
    "Does phones1 rhyme with phones2?"
    i1, i2 = find_rime(phones1), find_rime(phones2)
    return (phones1[i1:] == phones2[i2:]
            and phones1[i1-1:i1] != phones2[i2-1:i2])

def find_rime(phones):
    "Return the position of the stressed vowel starting phones's rime."
    for i in range(len(phones)-1, 0, -1):
        if phones[i][-1] in '12':
            return i
    return 0


def pronounce(words):
    return [phone for word in words for phone in pronunciations[word]]

pronunciations = {}
for line in open('cmudict.0.7a'):
    if ';;' in line or not line.strip(): continue
    word, phones = line.split(None, 1)
    if word.endswith(')'): continue # Ignore alternative pronunciations, for now
    pronunciations[word.lower()] = tuple(phones.split())
vocabulary = pronunciations.keys()


if __name__ == '__main__':
    sys.exit(main(sys.argv))