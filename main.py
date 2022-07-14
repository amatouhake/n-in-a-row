import tkinter as tk
from tkinter import ttk, messagebox
import numpy as np
from math import floor
from itertools import product
from string import ascii_uppercase, digits, punctuation
from typing import Any, Callable


class Config:
    signs = "OX"
    shape = [4, 4]
    n_in_a_row = 4
    n_player = 2
    n_row = 1
    space_size = 64
    border_size = 1
    show_coordinates = True


class Main(ttk.Frame):
    def __init__(self, *args: tuple[Any], **kargs: dict[str, Any]) -> None:
        super().__init__(*args, **kargs, padding=100)

        button = ttk.Button(self, text="スタート")
        button.bind("<1>", self.start_game)
        button.pack()

    def start_game(self, event: tk.Event = None) -> None:
        Config.signs += "".join(
            set((ascii_uppercase + digits + punctuation).strip(Config.signs))
        )

        Config.space_size = min(
            Config.space_size,
            floor(min(
                self.winfo_screenwidth() / np.product(Config.shape[::2]),
                self.winfo_screenheight() / np.product(Config.shape[1::2])
            ) * 0.8)
        )

        if Config.n_player <= len(Config.signs):
            self.destroy()
            Game(self.master).pack()
        else:
            messagebox.showwarning("警告", "プレイヤーが多すぎます")


class Game(ttk.Frame):
    def __init__(self, *args: tuple[Any], **kargs: dict[str, Any]) -> None:
        super().__init__(*args, **kargs)

        self.player = 1
        self.rows = dict(zip(range(Config.n_player), [0] * (Config.n_player)))

        self.board = Board(self)
        self.board.pack()

        self.status = Status(self)
        self.status.pack()

        button = ttk.Button(self, text="中断")
        button.bind("<1>", self.start_main)
        button.pack()

    def start_main(self, event: tk.Event = None) -> None:
        self.destroy()
        Main(self.master).pack()

    def on_left_click_space(self, event: tk.Event) -> None:
        sign = Config.signs[self.player - 1]
        space = event.widget

        space.player = self.player
        space.label = ttk.Label(
            space,
            anchor="center",
            background="light gray",
            text=sign,
            border=Config.border_size,
            relief="solid"
        )
        space.label.place(
            x=-1,
            y=-1,
            width=Config.space_size,
            height=Config.space_size
        )

        raveled_spaces = np.ravel(self.board.spaces)

        if(Config.show_coordinates):
            print(sign, space.coordinates)

        for i in range(Config.n_in_a_row):
            def generate_coordinate(dimension):
                coordinate = space.coordinates[dimension]
                diff = i + 1
                stop_plus = coordinate + diff
                stop_minus = coordinate - diff
                return [
                    range(stop_plus - Config.n_in_a_row, stop_plus),
                    [space.coordinates[dimension]] * Config.n_in_a_row,
                    range(stop_minus + Config.n_in_a_row, stop_minus, -1)
                ]

            coordinate_products = list(product(
                *[generate_coordinate(d) for d in range(len(Config.shape))]
            ))

            for coordinate_product in coordinate_products[:int((len(coordinate_products) - 1) / 2)]:
                coordinates_set = set(zip(*coordinate_product))
                if coordinates_set <= {s.coordinates for s in raveled_spaces if s.player == space.player}:
                    self.rows[self.player - 1] += 1
                    for coordinates in coordinates_set:
                        self.board.spaces[coordinates].label["background"] = "light sky blue"

        if self.rows[self.player - 1] == Config.n_row:
            messagebox.showinfo("終了", f"{sign}の勝ち")
            self.start_main()
        elif not [s for s in raveled_spaces if s.player == 0]:
            messagebox.showinfo("終了", "引き分け")
            self.start_main()
        else:
            self.status.player_value.labels[self.player - 1].turn_off()
            self.player = 1 if self.player == Config.n_player else self.player + 1
            self.status.player_value.labels[self.player - 1].turn_on()


class Status(ttk.Frame):
    def __init__(self, *args: tuple[Any], **kargs: dict[str, Any]) -> None:
        super().__init__(*args, **kargs, padding=10)

        self.player_key = ttk.Label(self, text="プレイヤー")
        self.player_value = PlayerValue(self)

        self.player_key.grid(row=0, column=0)
        self.player_value.grid(row=0, column=1)

        self.n_in_a_row_key = ttk.Label(self, text="n目並べ")
        self.n_in_a_row_value = ttk.Label(self, text=f"{Config.n_in_a_row}")

        self.n_in_a_row_key.grid(row=1, column=0)
        self.n_in_a_row_value.grid(row=1, column=1)


class PlayerValue(ttk.Frame):
    def __init__(self, *args, **kargs) -> None:
        super().__init__(*args, **kargs)
        self._labels = [
            PlayerValueLabel(self, player=i)
            for i in range(Config.n_player)
        ]
        self._labels[0].turn_on()

    @property
    def labels(self):
        return self._labels


class PlayerValueLabel(ttk.Label):
    def __init__(self, *args: tuple[Any], player: int, **kargs: dict[str, Any]) -> None:
        super().__init__(*args, **kargs, text=Config.signs[player], padding=5)
        self.grid(row=0, column=player)

    def turn_on(self):
        self["relief"] = "solid"
        self["background"] = "light gray"

    def turn_off(self):
        self["relief"] = ""
        self["background"] = ""


class Space(ttk.Frame):
    def __init__(self, *args: tuple[Any], coordinates: tuple, callback: Callable[[Game, tk.Event], Any], **kargs: dict[str, Any]) -> None:
        super().__init__(*args, **kargs, width=Config.space_size, height=Config.space_size)
        self._coordinates = coordinates
        self._player = 0
        self.bind("<1>", callback)

    @property
    def coordinates(self) -> tuple:
        return self._coordinates

    @property
    def player(self) -> None:
        return self._player

    @player.setter
    def player(self, player) -> None:
        self._player = player

    @property
    def label(self) -> None:
        return self._label

    @label.setter
    def label(self, label) -> None:
        self._label = label


class SpaceFrame(ttk.Frame):
    def generate_spaces(self, shape: tuple, coordinates: tuple, callback: Callable[[Game, tk.Event], Any]) -> None:
        shape_length = len(shape)
        is_even = shape_length % 2 == 0

        if shape_length > 2:
            if is_even:
                for row in range(shape[-1]):
                    for column in range(shape[-2]):
                        space_frame = SpaceFrame(
                            self,
                            width=Config.space_size * np.prod(shape[:-4:-2]),
                            height=Config.space_size * np.prod(shape[:-3:-2]),
                            border=Config.border_size,
                            relief="solid"
                        )
                        space_frame.grid(row=row, column=column)
                        for space in space_frame.generate_spaces(shape[:-2], (column, row) + coordinates, callback):
                            yield space
            else:
                for column in range(shape[-1]):
                    space_frame = SpaceFrame(
                        self,
                        width=Config.space_size * np.prod(shape[:-3:-2]),
                        height=Config.space_size * np.prod(shape[:-2:-2]),
                        border=Config.border_size,
                        relief="solid"
                    )
                    space_frame.grid(row=0, column=column)
                    for space in space_frame.generate_spaces(shape[:-1], (column,) + coordinates, callback):
                        yield space
        else:
            if is_even:
                for row in range(shape[-1]):
                    for column in range(shape[-2]):
                        space = Space(
                            self,
                            coordinates=(column, row) + coordinates,
                            callback=callback,
                            border=Config.border_size,
                            relief="solid"
                        )
                        space.grid(row=row, column=column)
                        yield space
            else:
                for column in range(shape[-1]):
                    space = Space(
                        self,
                        coordinates=(column,) + coordinates,
                        callback=callback,
                        border=Config.border_size,
                        relief="solid"
                    )
                    space.grid(row=0, column=column)
                    yield space


class Board(SpaceFrame):
    def __init__(self, *args: tuple[Any], **kargs: dict[str, Any]) -> None:
        super().__init__(*args, **kargs)
        self._spaces = np.reshape(sorted(list(self.generate_spaces(
            Config.shape, (), self.master.on_left_click_space
        )), key=lambda x: x.coordinates), Config.shape)

    @property
    def spaces(self):
        return self._spaces


def main() -> None:
    root = tk.Tk()
    root.title("n目並べ")
    root.resizable(width=False, height=False)
    Main(root).pack()
    root.mainloop()


if __name__ == "__main__":
    main()
