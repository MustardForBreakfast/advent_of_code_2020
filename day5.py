import typing as t
from enum import Enum
import re


ROWS = 128
COLS = 8


class RowPick(Enum):
    LOWER = "F"
    UPPER = "B"


class ColPick(Enum):
    LOWER = "L"
    UPPER = "R"


# ***** Parsing helpers *****

def row_picks(row_hash: str) -> t.Tuple[RowPick, ...]:
    """ First 7 characters -> RowPicks."""
    return tuple(map(lambda c: RowPick(c), list(row_hash)))


def col_picks(col_hash: str) -> t.Tuple[ColPick, ...]:
    """ Last 3 characters -> ColPicks."""
    return tuple(map(lambda c: ColPick(c), list(col_hash)))


def parse_picks(
    seat_hash: str
) -> t.Tuple[t.Tuple[RowPick, ...], t.Tuple[ColPick]]:
    """Break the hash into row and col components, parse into enums."""
    groups = re.search('^([FB]{7})([LR]{3})$', seat_hash)
    return (row_picks(groups[1]), col_picks(groups[2]))


# ***** Filtering algo *****

def generate_next_range(
    current_range: t.Iterable,
    pick: t.Union[RowPick, ColPick]
) -> t.Iterable:
    """Discard the appropriate half of a range, return what's left."""
    length = len(current_range)
    if pick in (RowPick.LOWER, ColPick.LOWER):
        return current_range[:length//2]

    return current_range[length//2:]


def _find_row_or_column_number(
    picks: t.Tuple[t.Union[RowPick, ColPick], ...],
    total_count: int
) -> int:
    """Find a row or column coordinate by recursively eliminating other possibilities."""

    def _get_number_or_next_range(
        current_range: t.Iterable[int],
        picks: t.Tuple[t.Union[RowPick, ColPick], ...]
    ) -> t.Union[int, t.Iterable[int]]:
        """Recursively dig through progressively smaller ranges until only one number remains."""
        if len(current_range) == 1:
            # return if we've found the row or column number
            return current_range[0]

        next_pick = picks[0]
        next_range = generate_next_range(current_range, next_pick)
        return _get_number_or_next_range(next_range, picks[1:])

    start_range = range(0, total_count)
    return _get_number_or_next_range(start_range, picks)


def find_row(row_picks: t.Tuple[RowPick, ...]) -> int:
    """Find a row coordinate."""
    return _find_row_or_column_number(row_picks, ROWS)


def find_col(col_picks: t.Tuple[ColPick, ...]) -> int:
    """Find a column coordinate."""
    return _find_row_or_column_number(col_picks, COLS)


def get_seat_coords(seat_hash: t.Tuple[str, ...]) -> t.Tuple[int, int]:
    """Given a hash, find the coordinates for a seat."""
    row_picks, col_picks = parse_picks(seat_hash)
    row_number = find_row(row_picks)
    col_number = find_col(col_picks)
    return (row_number, col_number)


def id_from_coords(row: int, col: int) -> int:
    """Calculate a seat ID from its coordinates."""
    return (row * 8) + col


def get_seat_id(seat_hash: str) -> int:
    """Given a hash, determine a seat ID."""
    row, col = get_seat_coords(seat_hash)
    return id_from_coords(row, col)


def calculate_occupied_ids(seat_hashes: t.Tuple[str, ...]) -> t.Tuple[int, ...]:
    """Figure out which seats in the plane have boarding passes."""
    return tuple(map(get_seat_id, seat_hashes))


def generate_all_ids(rows: int, cols: int) -> t.Tuple[int, ...]:
    """Generate all possible seat IDs for the plane."""
    ids = []
    for r in range(0, rows):
        for c in range(0, cols):
            ids.append(id_from_coords(r, c))
    return tuple(ids)


def get_unoccupied_seats(seat_hashes: t.Tuple[str, ...]) -> t.Tuple[str, ...]:
    """Subtract claimed/occupied seats from all possible seats."""
    all_ids = generate_all_ids(ROWS, COLS)
    occupied_ids = calculate_occupied_ids(seat_hashes)
    return tuple(set(all_ids) - set(occupied_ids))


def find_my_seat(seat_hashes: t.Tuple[str, ...]) -> int:
    """Given all seat hashes _but_ my own, determine my seat ID.

    Given information:
    - "all possible seats" will _overrepresent_ the number of seats in the plane.
    - My seat id _must_ have sequential neighbors in the plane, and those seats are occupied.
      e.g. (my_id + 1) and (my_id - 1) both exist and are claimed.
    - My seat id is the only unclaimed id that will fulfill this criteria.
    """
    unclaimed_seats = get_unoccupied_seats(seat_hashes)

    def _has_no_unclaimed_neighbors(id):
        return id + 1 not in unclaimed_seats and id - 1 not in unclaimed_seats

    remaining = tuple(filter(_has_no_unclaimed_neighbors, unclaimed_seats))
    return remaining[0]


# ALL_HASHES_BUT_MINE = [
#   'FBBBFBBLRR',
#   'BFFFBBFLRR',
#   'BFBFBBFLLR',
#   ...remaining challenge data goes here
# ]

# seat_id = find_my_seat(ALL_HASHES_BUT_MINE)
