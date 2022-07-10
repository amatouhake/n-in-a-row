import tkinter as tk
from tkinter import ttk
import numpy as np
from tkinter import messagebox
from itertools import product
from string import ascii_uppercase, digits, punctuation


def init_screen_start():
    global n_player

    def start(event: tk.Event):
        global n_player
        n_player = int(entry_n.get())
        init_screen_game()

    screen_start = tk.Tk()
    screen_start.title("n目並べ")
    screen_start.geometry("256x256")

    frame_n = tk.Frame(screen_start)
    frame_n.pack()

    label_n = tk.Label(frame_n, text="n")
    label_n.grid(row=0, column=0)

    entry_n = tk.Entry(frame_n)
    entry_n.insert(tk.END, n_player)
    entry_n.grid(row=0, column=1)

    button_start = tk.Button(screen_start, text="スタート")
    button_start.pack()
    button_start.bind("<1>", start)

    screen_start.mainloop()


# setup
player = 1

# config
n_in_a_row = 4
n_player = 2
shape = (2, 3, 4)

show_coordinates = True

space_size = 64

signs = "OX"
signs += "".join(set((ascii_uppercase + digits + punctuation).strip(signs)))


def init_screen_game():
    def generate_frame_spaces(frame_spaces: list, master: tk.Misc, shape: tuple, coordinates: tuple):
        def generate_frame_space(row: int, column: int):
            bd = np.ceil((shape_length + 1) / 2)
            frame_space = tk.Frame(
                master, width=space_size + bd, height=space_size + bd, bd=bd, relief="ridge"
            )
            frame_space.grid(row=row, column=column)
            frame_space.bind("<1>", on_left_click_frame_space)
            return frame_space

        shape_length = len(shape)

        if shape_length > 3:
            for row in range(shape[-1]):
                for column in range(shape[-2]):
                    frame = tk.Frame(master, width=space_size * np.prod(
                        shape[:-4:-2]), height=space_size * np.prod(shape[:-3:-2]), bd=1, relief="ridge")
                    frame.grid(row=row, column=column)
                    generate_frame_spaces(
                        frame_spaces, frame, shape[:-2], (column, row) + coordinates)

        elif shape_length == 3:
            for column in range(shape[2]):
                frame = tk.Frame(
                    master, width=space_size * shape[2], height=space_size * shape[1], bd=1, relief="ridge")
                frame.grid(row=0, column=column)
                generate_frame_spaces(
                    frame_spaces, frame, shape[:2], (column,) + coordinates)

        elif shape_length == 2:
            for row in range(shape[1]):
                for column in range(shape[0]):
                    frame_space = generate_frame_space(row, column)
                    frame_space.coordinates = (column, row) + coordinates
                    frame_spaces.append(frame_space)

        elif shape_length == 1:
            for column in range(shape[0]):
                frame_space = generate_frame_space(0, column)
                frame_space.coordinates = (column,) + coordinates
                frame_spaces.append(frame_space)

        return frame_spaces

    def set_title():
        screen_game.title(
            f"{len(shape)}次元{n_in_a_row}目並べ{n_player}人プレイ（{player}人目の{signs[player - 1]}のターン）")

    def on_wm_delete_window():
        global player
        player = 1
        screen_game.destroy()

    def on_left_click_frame_space(event: tk.Event):
        global player
        frame_space = event.widget
        coordinates = frame_space.coordinates
        sign = signs[player - 1]

        spaces[coordinates] = player
        label = tk.Label(frame_space, text=sign, bg="light gray")
        label.place(width=space_size, height=space_size)
        frame_space.label = label

        exit_flag = False

        if(show_coordinates):
            print(coordinates)

        for i in range(n_in_a_row):
            def generate_coordinate(dimension):
                stop_plus = coordinates[dimension] + i + 1
                stop_minus = coordinates[dimension] - i - 1
                return [
                    list(range(stop_plus - n_in_a_row, stop_plus)),
                    [coordinates[dimension]] * n_in_a_row,
                    list(range(stop_minus + n_in_a_row, stop_minus, -1))
                ]

            coordinate_products = list(product(
                *[generate_coordinate(d) for d in range(len(shape))]
            ))

            for coordinate_product in coordinate_products[:int((len(coordinate_products) - 1) / 2)]:
                coordinates_set = set(zip(*coordinate_product))
                if (coordinates_set <= set(zip(*np.asarray(spaces == player).nonzero()))):
                    exit_flag = True
                    for coordinates in coordinates_set:
                        frame_space_lined: tk.Frame = next(
                            (f for f in frame_spaces if f.coordinates == coordinates), None)
                        frame_space_lined.label["bg"] = "light sky blue"

        if exit_flag:
            messagebox.showinfo("終了", f"{sign}の勝ちです！")
            on_wm_delete_window()
        else:
            player = 1 if player == n_player else player + 1
            set_title()

    screen_game = tk.Tk()
    screen_game.resizable(False, False)
    screen_game.protocol("WM_DELETE_WINDOW", on_wm_delete_window)
    set_title()

    global space_size
    spacewidth = screen_game.winfo_screenwidth() // np.product(shape[::2])
    spaceheight = screen_game.winfo_screenheight() // np.product(shape[1::2])
    spacesize = spacewidth if spacewidth < spaceheight else spaceheight
    space_size = spacesize if spacesize < space_size else space_size
    space_size *= 0.9

    spaces = np.zeros(shape)
    frame_spaces = generate_frame_spaces([], screen_game, shape, ())

    screen_game.mainloop()


if __name__ == "__main__":
    # init_screen_start()
    init_screen_game()
