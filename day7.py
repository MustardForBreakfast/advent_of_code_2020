"""Day 7, parts 1 and 2."""
import re
import typing as t
from functools import reduce
from pathlib import Path


def _parse_container_contents(rule_line):
    """
    'light red bags contain 1 bright white bag, 2 muted yellow bags.' ->
    ('light red', '1 bright white bag, 2 muted yellow bags')
    """
    groups = re.search(r"^([a-z\s]+) bags contain (.+).$", rule_line)
    container = groups[1]
    contents = groups[2]

    return (container, contents)


def _parse_content_bag_and_count(content_str):
    """5 faded blue bags -> ('faded blue', 5)"""
    groups = re.search(r"^(\d) ([a-z\s]+) bags*$", content_str)
    return (groups[2], int(groups[1]))


def _parse_contents(contents_str):
    """
    '5 faded blue bags, 6 dotted black bags' ->
    (('faded blue', 5), ('dotted black', 6))

    'no other bags' -> ()
    """
    if contents_str == "no other bags":
        return ()
    splitstrip = tuple(map(lambda b: b.strip(), contents_str.split(",")))
    return tuple(map(lambda cb: _parse_content_bag_and_count(cb), splitstrip))


def parse_rule(rule_line: str) -> t.Tuple[str, t.Tuple[int, str]]:
    """
    'light red bags contain 1 bright white bag, 2 muted yellow bags.' ->
    ('light red', ((1, 'bright white'), (2, 'muted yellow')))

    'dotted black bags contain no other bags.' -> ('dotted black', ())
    """
    container, contents = _parse_container_contents(rule_line)
    contents_with_counts = _parse_contents(contents)
    return (container, contents_with_counts)


def _get_rules(data: str) -> t.Tuple[str, ...]:
    return tuple(data.split("\n"))


def parse_rules(data: str) -> t.Dict[str, t.Dict[str, int]]:
    """Transform input data into:
    {
        'light red': {
            'bright white': 1,
            'muted yellow': 2
        },
        'bright white': {
            'shiny gold': 1
        },
        'faded blue': {},
        ...
    }
    """
    rules = _get_rules(data)
    parsed = tuple(map(lambda r: parse_rule(r), rules))
    return reduce(lambda acc, r: {**acc, r[0]: dict(r[1])}, parsed, {})


def get_content_bag_count(target_bag: str, rules: t.Dict[str, t.Dict[str, int]]) -> int:
    bag = rules[target_bag]
    sum_top_contents = reduce(lambda acc, count: acc + count, bag.values(), 0)
    # return (sum_top_contents)
    sum_contents_contents = reduce(
        lambda acc, b_name: acc + (get_content_bag_count(b_name, rules) * bag[b_name]),
        bag.keys(),
        0,
    )
    return sum_top_contents + sum_contents_contents


# ***** Used in Part 1: *****
def can_contain(
    target_bag: str, possible_content_bag: str, rules: t.Dict[str, t.Dict[str, int]]
) -> bool:
    target = rules[target_bag]
    contents = target.keys()

    if possible_content_bag in contents:
        return True

    return any(map(lambda b: can_contain(b, possible_content_bag, rules), contents))


def get_bag_count(
    possible_content_bag: str, rules: t.Dict[str, t.Dict[str, int]]
) -> int:
    return len(
        tuple(
            filter(
                lambda b: b is True,
                map(
                    lambda b: can_contain(b, possible_content_bag, rules), rules.keys()
                ),
            )
        )
    )


def get_shiny_gold_container_count(data):
    rules = parse_rules(data)
    return get_bag_count("shiny gold", rules)


# ***************************


if __name__ == "__main__":
    DATA = Path("data/day7.txt").read_text()
    # solves part 1:
    print(get_shiny_gold_container_count(DATA))

    # solves part 2:
    rules = parse_rules(DATA)
    print(get_content_bag_count("shiny gold", rules))
