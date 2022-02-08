#!/usr/bin/env python3

"""Read a training log file and then dump out all rep maxes for all lifts.

My training log file is formatted like this:

2021-07-17
low-bar squat 5x290 3x325 0x365 3x345 3x325 3x310 5x290 5x270 20x250  FAIL
sumo deadlift 5x165 5x195 (3,5,7,4,6)x230 0x320
RDL (12,12,12)x175
kneeling ab wheel rollouts (32,32,32)
reverse Tyler twist right arm (15,15,15)

So an ISO-8601 datestamp
then one or more lines formatted like:
{exercise name} {sets with reps and weights} {maybe some random stuff}
Anything before the first number is the exercise name.
Anything after the last number is random noise that should be ignored.
Anything in between is sets and reps and weights.
Sometimes a set is reps x weight
Sometimes multiple sets at the same weight will be (reps),(reps),(reps)x(weight)
Sometimes multiple sets at the same weight will be (sets)x(reps)x(weight)
Sometimes there are only reps but no weight.
A # and anything after it in the line is a comment and ignored.
"""

import argparse
from math import exp
import re
import sys

from typing import Dict, IO, Tuple


date_pattern = r"^(\d\d\d\d-\d\d-\d\d)"
date_matcher = re.compile(date_pattern)
lift_pattern = r"^(\D*)(\d.*\d+)(.*)$"
lift_matcher = re.compile(lift_pattern)
reps_pattern = r"^(\d+)$"
reps_matcher = re.compile(reps_pattern)
multi_reps_pattern = r"^\((\d+,.*\d)\)$"
multi_reps_matcher = re.compile(multi_reps_pattern)
sets_x_reps_x_weight_pattern = r"^(\d+)x(\d+)x(-?\d+\.?-?\d*)$"
sets_x_reps_x_weight_matcher = re.compile(sets_x_reps_x_weight_pattern)
reps_x_weight_pattern = r"^(\d+)x(-?\d+\.?-?\d*)$"
reps_x_weight_matcher = re.compile(reps_x_weight_pattern)
multi_reps_x_weight_pattern = r"^\((\d+,.*\d)\)x(-?\d+\.?-?\d*)$"
multi_reps_x_weight_matcher = re.compile(multi_reps_x_weight_pattern)


def wathan_e1rm(reps: int, weight: float) -> float:
    if reps == 1:
        return weight
    if reps > 10:
        reps = 10
    return 100 * weight / (48.8 + 53.8 * exp(-0.075 * reps))


def add_to_rms(
    rms: Dict[str, Dict[float, Tuple[int, str, float]]],
    exercise: str,
    reps: int,
    weight: float,
    current_date: str,
) -> None:
    """Add a new rep max, if it is one."""
    if not reps or not exercise:
        return
    weight_to_reps_date = rms.get(exercise)
    if weight_to_reps_date is None:
        weight_to_reps_date = {}
        rms[exercise] = weight_to_reps_date
    previous_best_reps, _, _ = weight_to_reps_date.get(weight, (0, "", 0.0))
    if reps > previous_best_reps:
        weight_to_reps_date[weight] = (
            reps,
            current_date,
            wathan_e1rm(reps, weight),
        )


def remove_lesser_rms(
    rms: Dict[str, Dict[float, Tuple[int, str, float]]]
) -> None:
    for exercise, weight_to_reps_date in rms.items():
        weights_to_remove = set()
        for weight, (reps, date, e1rm) in weight_to_reps_date.items():
            for weight2, (reps2, date2, e1rm2) in weight_to_reps_date.items():
                if (
                    reps2 >= reps
                    and weight2 >= weight
                    and (reps2 > reps or weight2 > weight)
                ):
                    weights_to_remove.add(weight)
                    break
        for weight in weights_to_remove:
            del weight_to_reps_date[weight]


def output(
    exercise_to_rms: Dict[str, Dict[float, Tuple[int, str, float]]]
) -> None:
    for exercise in sorted(exercise_to_rms, key=str.casefold):
        print(exercise)
        inner_dict = exercise_to_rms[exercise]
        for weight, (reps, date, e1rm) in sorted(inner_dict.items()):
            print(f"    {weight:7.2f}: {reps:3}  {date}  {e1rm:6.1f}")


def read_weight_log(infile: IO, start_date: str, end_date: str) -> None:
    current_date = None
    # exercise_name: (weight, reps, e1rm)
    exercise_to_rms = (
        {}
    )  # type: Dict[str, Dict[float, Tuple[int, str, float]]]
    for line in infile:
        line = line.strip()
        if not line or line.startswith("#"):
            continue
        line = line.split("#")[0]
        match = date_matcher.search(line)
        if match:
            # Just a string for now, probably should be a datetime.date
            current_date = match.group(1)
        else:
            if not current_date or start_date and current_date < start_date:
                continue
            if end_date and current_date > end_date:
                break
            match = lift_matcher.search(line)
            if match:
                exercise = match.group(1)
                numbers = match.group(2)
                extra = match.group(3)
                if exercise.endswith("("):
                    exercise = exercise[:-1]
                    numbers = "(" + numbers
                if extra.startswith(")"):
                    extra = extra[1:]
                    numbers = numbers + ")"
                exercise = exercise.strip()
                numbers = numbers.strip()
                extra = extra.strip()
                terms = numbers.split()
                for term in terms:
                    term = term.strip(",")
                    match = reps_matcher.search(term)
                    if match:
                        reps = int(match.group(1))
                        weight = 0.0
                        add_to_rms(
                            exercise_to_rms,
                            exercise,
                            reps,
                            weight,
                            current_date,
                        )
                        continue
                    match = multi_reps_matcher.search(term)
                    if match:
                        blob = match.group(1)
                        parts = blob.split(",")
                        repses = list(map(int, parts))
                        weight = 0.0
                        add_to_rms(
                            exercise_to_rms,
                            exercise,
                            max(repses),
                            weight,
                            current_date,
                        )
                        continue
                    match = sets_x_reps_x_weight_matcher.search(term)
                    if match:
                        sets = int(match.group(1))
                        reps = int(match.group(2))
                        weight = float(match.group(3))
                        add_to_rms(
                            exercise_to_rms,
                            exercise,
                            reps,
                            weight,
                            current_date,
                        )
                        continue
                    match = reps_x_weight_matcher.search(term)
                    if match:
                        reps = int(match.group(1))
                        weight = float(match.group(2))
                        add_to_rms(
                            exercise_to_rms,
                            exercise,
                            reps,
                            weight,
                            current_date,
                        )
                        continue
                    match = multi_reps_x_weight_matcher.search(term)
                    if match:
                        blob = match.group(1)
                        parts = blob.split(",")
                        repses = list(map(int, parts))
                        weight = float(match.group(2))
                        add_to_rms(
                            exercise_to_rms,
                            exercise,
                            max(repses),
                            weight,
                            current_date,
                        )
                        continue
    remove_lesser_rms(exercise_to_rms)
    output(exercise_to_rms)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--weight-log-path",
        "-w",
        dest="weight_log_path",
        action="store",
        help="weight log path",
    )
    parser.add_argument(
        "--start-date",
        "-s",
        dest="start_date",
        action="store",
        help="start date",
    )
    parser.add_argument(
        "--end-date", "-e", dest="end_date", action="store", help="end date"
    )
    args = parser.parse_args()
    if args.weight_log_path:
        infile = open(args.weight_log_path)
    else:
        infile = sys.stdin
    read_weight_log(infile, args.start_date, args.end_date)


if __name__ == "__main__":
    main()
