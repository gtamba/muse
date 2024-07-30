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
        1: ("Db", "C#"),
        2: ("D", "D"),
        3: ("Eb", "D#"),
        4: ("E", "E"),
        5: ("F", "F"),
        6: ("Gb", "F#"),
        7: ("G", "G"),
        8: ("Ab", "G#"),
        9: ("A", "A"),
        10: ("Bb", "A#"),
        11: ("B", "B"),
    }
    BASE_TONES: tp.ClassVar[tp.List[str]] = [
        "C",
        "D",
        "E",
        "F",
        "G",
        "A",
        "B",
    ]
    A4_OFFSET = 57
    A4_FREQ = 440

    @classmethod
    def get_base_tones(cls, base):
        idx = cls.BASE_TONES.index(base)
        return cls.BASE_TONES[idx:] + cls.BASE_TONES[:idx]


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

    @property
    def base_tone(self):
        return self.note[0]

    def has_enharmonic(self) -> bool:
        return self.note in ("C#", "Db", "D#", "Eb", "F#", "Gb", "G#", "Ab", "A#", "Bb")

    def toggle_enharmonic(self, sharp=True) -> None:
        self.note = PitchMapping.INDEX_TO_PITCHES[self._offset_c0 % 12][int(sharp)]

    # TODO: Handle enharmonics
    def step(self, semitones: int, reset_octave=False) -> "Pitch":
        if semitones == 0:
            return self
        target = self._offset_c0 + semitones

        if target < 0:
            raise ArithmeticError("Cannot step below C0")

        octave = self.octave if reset_octave else target // 12
        new_note = PitchMapping.INDEX_TO_PITCHES[target % 12][0]

        return Pitch(
            note=new_note,
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
    SHORT_NAMES_TO_INTERVALS: tp.ClassVar[tp.Mapping[str, int]] = {
        "P1": 0,
        "m2": 1,
        "M2": 2,
        "m3": 3,
        "M3": 4,
        "P4": 5,
        "TT": 6,
        "P5": 7,
        "m6": 8,
        "M6": 9,
        "m7": 10,
        "M7": 11,
        "P8": 12,
    }
    interval: int

    @classmethod
    def from_name(cls, name: str) -> "Interval":
        return cls(cls.SHORT_NAMES_TO_INTERVALS[name])

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
        base_tones = PitchMapping.get_base_tones(self.root.base_tone)

        for idx, interval in enumerate(sequence):
            step = pitches[-1].step(interval, reset_octave=True)
            if idx != len(sequence) - 1:
                if step.base_tone != base_tones[idx + 1]:
                    step.toggle_enharmonic(sharp=True)
            pitches.append(step)
        self.pitches = pitches
        self.tones = [pitch.note for pitch in self.pitches]

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


@dataclass
class Guitar:
    tuning: tp.Sequence[Pitch] = dataclasses.field(
        default_factory=lambda: [
            Pitch("E", 2),
            Pitch("A", 2),
            Pitch("D", 3),
            Pitch("G", 3),
            Pitch("B", 3),
            Pitch("E", 4),
        ]
    )
    n_frets: int = 24

    def __post_init__(self):
        self.fretboard = []

        for string in self.tuning:
            self.fretboard.append(
                [string.step(fret) for fret in range(self.n_frets + 1)]
            )

    def __getitem__(self, string):
        string = len(self.tuning) - string
        return self.fretboard[string]


if __name__ == "__main__":
    scale = ScaleSequence(Pitch("E", 2), "MAJOR")
    print(scale.tones)
