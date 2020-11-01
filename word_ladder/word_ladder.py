from word_ladder.compile_words import read_words
from word_ladder.types import WordDict
from word_ladder.utilities import get_word_with_letter_missing

from dataclasses import dataclass
from typing import Dict, Sequence, Iterable, Optional, List, Tuple


def get_neighbors(word: str, words: WordDict) -> Sequence[str]:
    """
    >>> words = {'?og': ['dog', 'log', 'fog'], 'd?g': ['dog', 'dig'], 'do?': ['dog'], 'l?g': ['log'], 'lo?': ['log']}
    >>> get_neighbors('dig', words)
    ('dog', 'dig')
    >>> get_neighbors('fog', words)
    ('dog', 'log', 'fog')
    """
    return tuple(
        neighbor
        for position in range(len(word))
        for neighbor in words.get(get_word_with_letter_missing(word, position), [])
    )

@dataclass(frozen=True)
class Rung:
    previous: Optional['Rung']
    words: Iterable[str]
    path: Dict[str, Iterable[str]]

def get_all_previous_words(rung: Rung) -> List[str]:
    """
    >>> rung_0 = Rung(None, ['dig'], {})
    >>> path = {'dog': ('log', 'fog', 'dig', 'dug', 'don', 'dob'), 'fig': ('dig', 'fog', 'fin')}
    >>> words = ['dob', 'don', 'dug', 'fin', 'fog', 'log']
    >>> rung_1 = Rung(rung_0, words, path)
    >>> sorted(get_all_previous_words(rung_1))
    ['dig', 'dob', 'don', 'dug', 'fin', 'fog', 'log']
    """
    return list(rung.words) + (get_all_previous_words(rung.previous) if rung.previous else [])

def get_next_rung(previous_rung: Rung, words: WordDict) -> Rung:
    """
    >>> from word_ladder.compile_words import add_to_words_dict
    >>> words = {}
    >>> for w in ['dog', 'log', 'fog', 'dig', 'dug', 'dim', 'don', 'dob', 'lug', 'fin']:
    ...     words = add_to_words_dict(words, w)
    >>> rung = Rung(None, ['dog', 'fig'], {})
    >>> next_rung = get_next_rung(rung, words)
    >>> next_rung.path
    {'dog': ('log', 'fog', 'dig', 'dug', 'don', 'dob'), 'fig': ('dig', 'fog', 'fin')}
    >>> sorted(next_rung.words)
    ['dig', 'dob', 'don', 'dug', 'fin', 'fog', 'log']
    """
    previous_words = get_all_previous_words(previous_rung)
    path = {
        source_word: tuple(w for w in get_neighbors(source_word, words) if w not in previous_words)
        for source_word in previous_rung.words
    }
    word_soup = frozenset(w for these_words in path.values() for w in these_words)
    return Rung(previous_rung, word_soup, path)

def get_key_for_value(d: Dict[str, Iterable[str]], value: str) -> str:
    """
    >>> d = {'a': ['x', 'y', 'z'], 'b': ['l', 'm'], 'c': ['t', 'u']}
    >>> get_key_for_value(d, 'y')
    'a'
    >>> get_key_for_value(d, 'u')
    'c'
    """
    for key, values in d.items():
        if value in values:
            return key

def get_ladder(rung: Rung, word: str):
    """
    >>> rung_0 = Rung(None, ['dig'], {'dig': ('dog', 'log')})
    >>> path = {'dog': ('log', 'fog', 'dig', 'dug', 'don', 'dob'), 'fig': ('dig', 'fog', 'fin')}
    >>> words = ['dig', 'dob', 'don', 'dug', 'fin', 'fog', 'log']
    >>> rung_1 = Rung(rung_0, words, path)
    >>> get_ladder(rung_1, 'fin')
    ['dig', 'fig', 'fin']
    """
    previous_word = get_key_for_value(rung.path, word)
    return (get_ladder(rung.previous, previous_word) if rung.previous else [previous_word]) + [word]

def get_start_and_target_words(words: WordDict) -> Tuple[str, str]:
    all_words = {w for word_list in words.values() for w in word_list}

    while True:
        start_word = input('Enter the starting word: ').lower()
        rung = Rung(None, [start_word], {})
        rung = get_next_rung(rung, words)
        if len(rung.words):
            break
        print(f'Sorry, there are no words next to "{start_word}". Choose another word.')

    while True:
        target_word = input('Enter the target word (if any): ').lower()
        if len(target_word) == 0:
            break
        if target_word in all_words:
            if len(target_word) == len(start_word):
                break
            else:
                print('Please choose a target word with the same length as the start word.')
        else:
            print('Please choose a word in the dictionary.')
    return (start_word, target_word)


if __name__ == '__main__':
    path = './data/words.txt'
    words = read_words(path)

    start_word, target_word = get_start_and_target_words(words)
    rung = Rung(None, [start_word], {})

    counter = 0
    while target_word not in rung.words and len(rung.words) > 0:
        rung = get_next_rung(rung, words)
        counter += 1
        print(f'Round {counter}: {len(rung.words):3} possible words, eg. {", ".join(sorted(rung.words)[:6])}')

    if len(rung.words) == 0:
        if (target_word):
            print('Could not do it!')
        print(f'Final words: {", ".join(sorted(rung.previous.words))}')
        exit()

    print()
    print(' → '.join([f'{w}' for w in get_ladder(rung, target_word)]))
    print()