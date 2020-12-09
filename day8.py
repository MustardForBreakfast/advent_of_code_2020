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


class LoopDetectedError(Exception):
    pass


class RemediationError(Exception):
    pass


def dump_instruction(inst: t.Tuple[str, int]) -> str:
    """Dump a parsed instruction to a line of data"""
    action, count = inst
    sign = "+" if count >= 0 else ""
    return f"{action} {sign}{count}"


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

    @property
    def is_final(self) -> bool:
        """Return whether this state is off the end of the instruction set."""
        return self.cur_index >= len(self.program)

    def get_next(self) -> "ProgramState":
        """Run the pending instruction to get the next program state."""
        if self.is_final:
            raise ValueError("can not get next of final State!")

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
    indexes_seen: t.List[int]

    @classmethod
    def from_instructions(cls, instructions: t.Tuple[str, ...]) -> "Program":
        return cls(
            state=ProgramState.get_initial(instructions),
            indexes_seen=[],
        )

    @property
    def accum(self):
        return self.state.cur_amount

    @property
    def pointer(self):
        return self.state.cur_index

    @property
    def is_complete(self):
        return self.state.is_final

    def log_index(self):
        """Record the current index.

        Warning: not idempotent for part 2!
        """
        self.indexes_seen.append(self.pointer)

    @staticmethod
    def _flip_action(inst: str) -> str:
        flipped = {"nop": "jmp", "jmp": "nop"}
        return flipped[inst]

    def _attempt_remediated_run(self):
        """Attempt to repair the program instructions and return a value."""
        orig_program = self.state.program
        pointer_index = self.indexes_seen.index(self.pointer)
        # fmt: off
        loop_cycle = self.indexes_seen[pointer_index:]
        # fmt: on
        bad_ops = ("nop", "jmp")
        nop_jmp = tuple(
            filter(
                lambda i: ProgramState._parse_instruction(orig_program[i])[0]
                in bad_ops,
                loop_cycle,
            )
        )

        for i in nop_jmp:
            # TODO: move this util out of the class
            action, count = ProgramState._parse_instruction(orig_program[i])
            flipped = self._flip_action(action)
            flipped_instruction = dump_instruction((flipped, count))

            repaired = list(orig_program + ())
            repaired[i] = flipped_instruction

            pgrm_repaired = self.from_instructions(tuple(repaired))

            try:
                # We want this to error out if it finds a loop again
                return pgrm_repaired.run(remediation_mode=False)

            except LoopDetectedError:
                pass

        raise RemediationError("Failed to remediate.")

        return self.accum

    def run(self, remediation_mode=False) -> int:
        """Run through the program and return the accumulator at the final state.

        If run in remediation_mode, attempt to repair the program in the event a
        loop is detected and return the result of the repaired program's run.
        """
        if self.pointer in self.indexes_seen:
            if not remediation_mode:
                raise LoopDetectedError(
                    "Loop detected, terminating before re-entry. index: "
                    f"{self.pointer}, accum: {self.accum}"
                )
            # TODO: trigger remediation behavior here.
            print(
                f"Loop detected at index {self.pointer}. Attempting to "
                "remediate and continue."
            )
            return self._attempt_remediated_run()

        if self.is_complete:
            print("Program complete.")
            return self.accum

        self.log_index()
        self.state = self.state.get_next()
        return self.run(remediation_mode)


if __name__ == "__main__":
    instructions = parse_to_lines("data/day8.txt")
    program = Program.from_instructions(instructions)
    result = program.run(True)
    print(result)
