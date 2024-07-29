import dataclasses
from dataclasses import dataclass
import typing as tp
from class_only_design import ClassOnly


class PitchMapping(ClassOnly):
    PITCHES_TO_INDEX: tp.ClassVar[tp.Mapping[str, int]] = {
        "C": 0,
        "B#": 0,
        "C#": 1,
        "Db": 1,
        "D": 2,
        "D#": 3,
        "Eb": 3,
        "E": 4,
        "Fb": 4,
        "F": 5,
        "E#": 5,
        "F#": 6,
        "Gb": 6,
        "G": 7,
        "G#": 8,
        "Ab": 8,
        "A": 9,
        "A#": 10,
        "Bb": 10,
        "B": 11,
        "Cb": 11,
    }

    # tuple to handle enharmonics, first example is the sharp version, second is the flat version
    INDEX_TO_PITCHES: tp.ClassVar[tp.Mapping[int, str]] = {
        0: ("C", "C"),
        1: ("C#", "Db"),
        2: ("D", "D"),
        3: ("D#", "Eb"),
        4: ("E", "F"),
        5: ("F", "F"),
        6: ("F#", "Gb"),
        7: ("G", "G"),
        8: ("G#", "Ab"),
        9: ("A", "A"),
        10: ("A#", "Bb"),
        11: ("B", "B"),
    }

    A4_OFFSET = 57
    A4_FREQ = 440


@dataclass
class Pitch:
    note: str
    octave: int = 4

    def __post_init__(self):
        if self.note not in PitchMapping.PITCHES_TO_INDEX:
            raise ValueError(f"Invalid note: {self.note}")
        self._offset_c0 = PitchMapping.PITCHES_TO_INDEX[self.note] + 12 * self.octave
        offset_a4 = self._offset_c0 - PitchMapping.A4_OFFSET
        self._freq = PitchMapping.A4_FREQ * (2 ** (offset_a4 / 12.0))

    def __sub__(self, other) -> int:
        return self._offset_c0 - other._offset_c0

    def __str__(self):
        return f"{self.note}{self.octave}"

    def __repr__(self):
        return f"{self.note}{self.octave}"

    @property
    def freq(self):
        return self._freq

    # TODO: Handle enharmonics
    def step(self, semitones: int, reset_octave=False) -> "Pitch":
        if semitones == 0:
            return self
        target = self._offset_c0 + semitones

        if target < 0:
            raise ArithmeticError("Cannot step below C0")

        octave = self.octave if reset_octave else target // 12
        return Pitch(
            note=PitchMapping.INDEX_TO_PITCHES[target % 12][0 if semitones > 0 else -1],
            octave=octave,
        )


@dataclass
class Interval:
    SHORT_NAMES: tp.ClassVar[tp.Mapping[int, str]] = {
        0: "P1",
        1: "m2",
        2: "M2",
        3: "m3",
        4: "M3",
        5: "P4",
        6: "TT",
        7: "P5",
        8: "m6",
        9: "M6",
        10: "m7",
        11: "M7",
        12: "P8",
    }
    LONG_NAMES: tp.ClassVar[tp.Mapping[int, str]] = {
        0: "Unison",
        1: "Minor Second",
        2: "Major Second",
        3: "Minor Third",
        4: "Major Third",
        5: "Perfect Fourth",
        6: "Tritone",
        7: "Perfect Fifth",
        8: "Minor Sixth",
        9: "Major Sixth",
        10: "Minor Seventh",
        11: "Major Seventh",
        12: "Octave",
    }

    interval: int

    @property
    def name(self, short=True):
        # TODO : Handle octave
        offset = self.interval if self.interval < 0 else 12 - self.interval

        return self.SHORT_NAMES[offset] if short else self.LONG_NAMES[offset]


@dataclass
class ScaleSequence:
    SCALES: tp.ClassVar[tp.Mapping[str, tp.Sequence[int]]] = {
        "MAJOR": (2, 2, 1, 2, 2, 2, 1),
        "IONION": (2, 2, 1, 2, 2, 2, 1),
        "DORIAN": (2, 1, 2, 2, 2, 1, 2),
        "PHRYGIAN": (1, 2, 2, 2, 1, 2, 2),
        "LYDIAN": (2, 2, 2, 1, 2, 2, 1),
        "MIXOLYDIAN": (2, 2, 1, 2, 2, 1, 2, 2),
        "AEOLIAN": (2, 1, 2, 2, 1, 2, 2),
        "MINOR": (2, 1, 2, 2, 1, 2, 2),
        "LOCRIAN": (1, 2, 2, 1, 2, 2, 2),
    }

    root: Pitch
    sequence: dataclasses.InitVar[tp.Union[tp.Sequence[int], str]] = "MAJOR"

    def __post_init__(self, sequence):
        if isinstance(sequence, str):
            if sequence.upper() not in self.SCALES:
                raise ValueError(f"Invalid Scale Description : {sequence}")
            sequence = self.SCALES[sequence.upper()]
        pitches = [self.root]
        for interval in sequence:
            pitches.append(pitches[-1].step(interval, reset_octave=True))
        self.pitches = pitches

    @property
    def triads(self, extended=False):
        n = len(self.pitches)
        for i in range(n - 1):
            if extended:
                yield self.pitches[i], self.pitches[(i + 2) % n], self.pitches[
                    (i + 4) % n
                ], self.pitches[(i + 6) % n]

            else:
                yield self.pitches[i], self.pitches[(i + 2) % n], self.pitches[
                    (i + 4) % n
                ]


# class Intervals(ClassOnly):
#     UNISON = 0
#     MINOR_SECOND = 1
#     MAJOR_SECOND = 2
#     MINOR_THIRD = 3
#     MAJOR_THIRD = 4
#     PERFECT_FOURTH = 5
#     TRITONE = 6
#     PERFECT_FIFTH = 7
#     MINOR_SIXTH = 8
#     MAJOR_SIXTH = 9
#     MINOR_SEVENTH = 10
#     MAJOR_SEVENTH = 11
#     OCTAVE = 12

#     @classmethod
#     def interval_from_name(cls, name: str) -> int:
#         return {
#             "P1": cls.UNISON,
#             "m2": cls.MINOR_SECOND,
#             "M2": cls.MAJOR_SECOND,
#             "m3": cls.MINOR_THIRD,
#             "M3": cls.MAJOR_THIRD,
#             "P4": cls.PERFECT_FOURTH,
#             "TT": cls.TRITONE,
#             "P5": cls.PERFECT_FIFTH,
#             "m6": cls.MINOR_SIXTH,
#             "M6": cls.MAJOR_SIXTH,
#             "m7": cls.MINOR_SEVENTH,
#             "M7": cls.MAJOR_SEVENTH,
#             "P8": cls.OCTAVE,
#         }[name]

#     @classmethod
#     def name_from_interval(cls, interval: int, ascending=True) -> str:
#         if not ascending:
#             interval -= 12

#         return {
#             cls.UNISON: "P1",
#             cls.MINOR_SECOND: "m2",
#             cls.MAJOR_SECOND: "M2",
#             cls.MINOR_THIRD: "m3",
#             cls.MAJOR_THIRD: "M3",
#             cls.PERFECT_FOURTH: "P4",
#             cls.TRITONE: "TT",
#             cls.PERFECT_FIFTH: "P5",
#             cls.MINOR_SIXTH: "m6",
#             cls.MAJOR_SIXTH: "M6",
#             cls.MINOR_SEVENTH: "m7",
#             cls.MAJOR_SEVENTH: "M7",
#             cls.OCTAVE: "P8",
#         }[interval]


# class ScaleSequence(ClassOnly):
#     MAJOR_SCALE = (2, 2, 1, 2, 2, 2, 1)

#     @staticmethod
#     def shift_tonic(sequence: tp.Sequence[Pitch], mode: int) -> tp.List[Pitch]:
#         return sequence[mode - 1 :] + sequence[: mode - 1]

#     @classmethod
#     def major(cls, root: Pitch) -> tp.List[Pitch]:
#         out = [root]
#         for step in cls.MAJOR_SCALE:
#             out.append(out[-1].step(step))
#         return out


if __name__ == "__main__":
    scale = ScaleSequence(Pitch("C"), "MAJOR")
    print(scale.pitches)
    print([t for t in scale.extended_triads])
