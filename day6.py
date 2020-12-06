from pathlib import Path
import typing as t
from functools import reduce

# ***** Parsing utils for test data *****


def _get_groups(data: str) -> t.Tuple[str, ...]:
    return tuple(data.split('\n\n'))


def _parse_group(group: str) -> t.Tuple[str, ...]:
    return tuple(group.split('\n'))


def parse_groups(data: str) -> t.Tuple[t.Tuple[str, ...], ...]:
    groups = _get_groups(data)
    return tuple(map(lambda g: _parse_group(g), groups))


def unanimous_questions_for_group(group: t.Tuple[str, ...]) -> t.Tuple[str, ...]:
    people_in_group = len(group)
    answer_count = {}

    for person in group:
        questions = list(person)
        for q in questions:
            if answer_count.get(q) is not None:
                answer_count[q] = answer_count[q] + 1
            else:
                answer_count[q] = 1

    return tuple(
        filter(
            lambda q: answer_count[q] == people_in_group,
            answer_count.keys()
        )
    )


def count_group_questions(groups: t.Tuple[t.Tuple[str, ...], ...]) -> int:
    return reduce(lambda acc, g: acc + len(unanimous_questions_for_group(g)), groups, 0)


def count_all_questions(data: str) -> int:
    groups = parse_groups(data)
    return count_group_questions(groups)


if __name__ == "__main__":
    DATA = Path('data/day6.txt').read_text()
    print(count_all_questions(DATA))
