"""Solution for Day 8."""
import re
import typing as t
from dataclasses import dataclass

from utils.parse import parse_to_lines

"""
nop +0  | 1
acc +1  | 2, 8(!)
jmp +4  | 3
acc +3  | 6
jmp -3  | 7
acc -99 |
acc +1  | 4
jmp -4  | 5
acc +6  |

First, the nop +0 does nothing. Then, the accumulator is increased from 0 to 1
(acc +1) and jmp +4 sets the next instruction to the other acc +1 near the bottom.
After it increases the accumulator from 1 to 2, jmp -4 executes, setting the next
instruction to the only acc +3. It sets the accumulator to 5, and jmp -3 causes
the program to continue back at the first acc +1.


Immediately before the program would run an instruction a second time, the value
in the accumulator is 5.

Run your copy of the boot code. Immediately before any instruction is executed a
second time, what value is in the accumulator?
"""


@dataclass
class ProgramState:
    cur_amount: int
    cur_index: int  # before the instruction that lives here is run
    program: t.Tuple[str, ...]

    @classmethod
    def get_initial(cls, program: t.Tuple[str, ...]) -> "ProgramState":
        return ProgramState(cur_amount=0, cur_index=0, program=program)

    @staticmethod
    def _parse_instruction(line: str) -> t.Tuple[str, int]:
        """Parse an instruction form a line of data"""
        groups = re.search(r"^([a-z]{3})\s([+-]\d+)$", line)
        assert groups is not None

        return (groups[1], int(groups[2]))

    def get_next(self) -> "ProgramState":
        """Run the pending instruction to get the next program state."""
        action, amount = self._parse_instruction(self.program[self.cur_index])

        next_amount = None
        next_index = None

        if action == "acc":
            next_amount = self.cur_amount + amount
            next_index = self.cur_index + 1
        elif action == "jmp":
            next_amount = self.cur_amount
            next_index = self.cur_index + amount
        elif action == "nop":
            next_amount = self.cur_amount
            next_index = self.cur_index + 1
        else:
            raise ValueError(f"unknown action {action}")

        return ProgramState(
            cur_amount=next_amount,
            cur_index=next_index,
            program=self.program,
        )


@dataclass
class Program:
    state: ProgramState
    indexes_seen: set

    @classmethod
    def from_instructions(cls, instructions: t.Tuple[str, ...]) -> "Program":
        return cls(
            state=ProgramState.get_initial(instructions),
            indexes_seen=set(),
        )

    @property
    def accum(self):
        return self.state.cur_amount

    @property
    def pointer(self):
        return self.state.cur_index

    def log_index(self):
        self.indexes_seen.add(self.pointer)

    def run(self):
        """Run through the program until a loop is found, then print accumulator."""
        if self.pointer in self.indexes_seen:
            print(self.accum)
            return

        self.log_index()
        self.state = self.state.get_next()
        self.run()


if __name__ == "__main__":
    instructions = parse_to_lines("data/day8_example.txt")
    program = Program.from_instructions(instructions)
    program.run()
