from tkinter import *
import tkinter as tk
from itertools import cycle
from tkinter import font
from typing import NamedTuple
import time
import random

class Player(NamedTuple):
    label: str
    color: str
    cpu: bool
    name: str

class Move(NamedTuple):
    row: int
    col: int
    label: str = ""

BOARD_SIZE: int = 3
DEFAULT_PLAYERS = (
    Player(label = "X", color = "blue", cpu = False, name = "Player one"),
    Player(label = "O", color = "green", cpu = False, name = "Player two"),
)


class TicTacToeGame:
    def __init__(self, players = DEFAULT_PLAYERS, board_size = BOARD_SIZE) -> None:
        self.players_list = list(players)
        self._players = None
        self.board_size = board_size
        self.current_player = None
        self.winner_combo = []
        self._current_moves = []
        self._has_winner = False
        self._winning_combos = []
        self.cpu_moves = []
        self.player_moves = []
        self.hard_mode = True
        self._setup_board()

    def set_cpu_player(self, player_index: int, new_cpu_value: bool) -> None:
        """Takes a player index (0 or 1) and a bool value to indicate if a player should be cpu controlled then creates a new list of players with the updated cpu info and sets up a cycle to interate through the list of players.

        :param player_index: An int value to represent the first "0" or second "1" player
        :type player_index: int
        :param new_cpu_value: A bool value to represent if the supplied "player_index" is a cpu (Default value is "False")
        :type new_cpu_value: bool
        """
        old_player = self.players_list[player_index]
        updated_player = old_player._replace(cpu=new_cpu_value)
        self.players_list[player_index] = updated_player
        self._players = cycle(self.players_list)
        
    def set_players(self, players) -> None:
        """Sets up a cycle to iterate through the list of players and initializes the current player

        :param players: A list of player objects
        :type players: list
        """
        self._players = cycle(players)
        self.current_player = next(self._players)

    def _setup_board(self) -> None:
        """Inittializes the game board, creating a grid of "Move" objects and computing all possible winning combinations (self._get_winning_combos) for the current board.
        """
        self._current_moves = [
            [Move(row, col) for col in range(self.board_size)]
            for row in range(self.board_size)
        ]
        self._winning_combos = self._get_winning_combos()

    def _get_winning_combos(self) -> list:
        rows = [
            [(move.row, move.col) for move in row]
            for row in self._current_moves
        ]
        columns = [list(col) for col in zip(*rows)]
        first_diagonal = [row[i] for i, row in enumerate(rows)]
        second_diagonal = [col[j] for j, col in enumerate(reversed(columns))]
        return rows + columns + [first_diagonal, second_diagonal]
    
    def is_valid_move(self, move):
        row, col = move.row, move.col
        move_was_not_played = self._current_moves[row][col].label == ""
        no_winner = not self._has_winner
        return no_winner and move_was_not_played
    
    def process_move(self, move):
        """Process the current move and check if it's a win."""
        row, col = move.row, move.col
        self._current_moves[row][col] = move
        for combo in self._winning_combos:
            results = set(
                self._current_moves[n][m].label
                for n, m in combo
            )
            is_win = (len(results) == 1) and ("" not in results)
            if is_win:
                self._has_winner = True
                self.winner_combo = combo
                break
    
    def has_winner(self):
        """Return True if the game has a winner, and False otherwise."""
        return self._has_winner
    
    def is_tied(self):
        """Return True if the game is tied, and False otherwise"""
        no_winner = not self._has_winner
        played_moves = (
            move.label for row in self._current_moves for move in row
        )
        return no_winner and all(played_moves)
    
    def toggle_player(self):
        """Return a toggled player."""
        self.current_player = next(self._players)

    def reset_game(self):
        """Reset the game state to play again."""
        for row, row_content in enumerate(self._current_moves):
            for col, _ in enumerate(row_content):
                row_content[col] = Move(row, col)
        self._has_winner = False
        self.hard_mode = True
        self.winner_combo = []
        self.cpu_moves = []
        self.player_moves = []
        self.players_list = list(DEFAULT_PLAYERS)
        self.current_player = DEFAULT_PLAYERS[0]


class TicTacToeBoard(tk.Tk):
    def __init__(self, game) -> None:
        super().__init__()
        self.minsize(400,500)
        self.title("Tic-Tac-Toe Game")
        self.master_frame = tk.Frame(master=self)
        self.master_frame.place(x=0, y=0, relheight=1, relwidth=1)
        self._cells = {}
        self._game = game
        self.twitch_check = "Hello"
        self.player_one_score = 0
        self.player_two_score = 0
        self.vs_cpu_status = None
        self.vs_cpu_info = [int, bool]
        self.twitch_vs_cpu_info = None
        self.hard_mode_status = self._game.hard_mode
        self.eval("tk::PlaceWindow . center")
        self.popup()
        self._create_board_display()
        self._create_board_grid()
        self._create_menu()

    def popup(self) -> None:
        self.cpu_mode_option = tk.IntVar()
        self.easy_mode_option = tk.IntVar()
        self.twitch_mode_option = tk.IntVar()
        self.first_player_mode_option = tk.IntVar()
        self.twitch_channel_input = None
        self.popup_window = tk.Toplevel()
        self.eval(f"tk::PlaceWindow {str(self.popup_window)} center")
        self.popup_window.title("Popup")
        self.popup_window.attributes("-topmost", True)
        self.popup_window.bind("<FocusOut>", lambda event: self.popup_window.focus_force())
        self.popup_window.protocol('WM_DELETE_WINDOW', 'break')
        self.popup_window.cpu_check = tk.Checkbutton(
            self.popup_window, 
            text="Play VS the CPU",
            variable=self.cpu_mode_option,
            onvalue=1,
            offvalue=0,
            command=self.vs_cpu_options,
            font=("helvetica", 13)).pack(pady=(5),padx=(20))
        self.popup_window.twitch_check = tk.Checkbutton(
            self.popup_window, 
            text="Twitch Plays DNT",
            variable=self.twitch_mode_option,
            onvalue=1, 
            offvalue=0,
            font=("helvetica", 13),
            command=self.channel_input).pack(pady=(5),padx=(20))
        self.popup_window.confirm_button = tk.Button(
            self.popup_window, 
            text="Confirm", 
            command=self.confirm_button,
            font=("helvetica", 13)).pack(side="bottom", padx=10,pady=10)
        self.attributes("-disabled", True)

    def channel_input(self):
        if self.twitch_mode_option.get():
            if self.twitch_channel_input is None:
                self.twitch_channel_input = tk.Entry(self.popup_window, width=20)
                self.twitch_channel_input.pack()
                self.twitch_channel_value_info = tk.Label(self.popup_window)
                self.twitch_channel_value_info.pack()
                self.twitch_channel_input.insert(tk.END, "Enter Twitch Channel")
                self.twitch_channel_input.bind("<FocusIn>", lambda e: self.text_entry_click())
                self.twitch_channel_input.bind("<FocusOut>", lambda e: self.on_text_entry_focusout())
                self.twitch_channel_input.config(fg= "grey")
        else:
            if self.twitch_channel_input is not None:
                self.twitch_channel_input.pack_forget()
                self.twitch_channel_input.destroy()
                self.twitch_channel_value_info.pack_forget()
                self.twitch_channel_value_info.destroy()
                self.twitch_channel_input = None
    
    def is_channel_input_valid(self):
        if self.twitch_value.lower() == "Holy".lower():
            return True
        else:
            return False

    def vs_cpu_options(self):
        if self.cpu_mode_option.get():
            self.first_player_check = tk.Checkbutton(
                self.popup_window, 
                text="Play First?",
                variable=self.first_player_mode_option,
                onvalue=1,
                offvalue=0,
                font=("helvetica", 13))
            self.first_player_check.pack(pady=(5),padx=(20))
            self.easy_mode_check = tk.Checkbutton(
                self.popup_window, 
                text="Easy Mode",
                variable=self.easy_mode_option,
                onvalue=1, 
                offvalue=0,
                font=("helvetica", 13))
            self.easy_mode_check.pack(pady=(5),padx=(20))
        else:
            self.first_player_check.pack_forget()
            self.first_player_check.destroy()
            self.easy_mode_check.pack_forget()
            self.easy_mode_check.destroy()

    def text_entry_click(self):
        if self.twitch_channel_input.get() == "Enter Twitch Channel":
            self.twitch_channel_input.delete(0, "end")
            self.twitch_channel_input.config(fg= "black")
    
    def on_text_entry_focusout(self):
        if self.twitch_channel_input.get() == "":
            self.twitch_channel_input.insert(tk.END, "Enter Twitch Channel")
            self.twitch_channel_input.config(fg= "grey")

    def confirm_button(self) -> None:
        if self.twitch_channel_input is not None:
            self.twitch_value = self.twitch_channel_input.get()
            if not self.is_channel_input_valid():
                self.twitch_channel_value_info["text"] = "No channels found"
                return
            elif self.is_channel_input_valid():
                pass
        
        self.attributes("-disabled", False)
        self.popup_window.destroy()
        label_msg = "Cpu"
        if self.easy_mode_option.get():
            self.hard_mode_status= False
        if self.cpu_mode_option.get() == 0:
            self._update_display(msg="Player one's turn")
            self.vs_cpu_status = False
            self._game.set_players(self._game.players_list)
            self._logic.cpu_play()
        else:
            if self.cpu_mode_option.get() and self.first_player_mode_option.get():
                self._update_display(msg="Player one's turn")
                self.vs_cpu_status = True
                self.vs_cpu_info = [1, True]
                self._update_player_two_info_display(label_msg)
                self._game.set_cpu_player(1, True)
                self._game.set_players(self._game.players_list)
                self._logic.cpu_play()
            elif self.cpu_mode_option.get() and self.first_player_mode_option.get() == 0:
                self.vs_cpu_status = True
                self.vs_cpu_info = [0, True]
                self._update_player_one_info_display(label_msg)
                self._game.set_cpu_player(0, True)
                self._game.set_players(self._game.players_list)
                print(type(self._game.players_list))
                self._logic.cpu_play()
        
    def _create_menu(self):
        menu_bar = tk.Menu(master=self)
        self.config(menu=menu_bar)
        file_menu = tk.Menu(master=menu_bar)
        file_menu.add_command(
            label="Play Again",
            command=self.restart_game,
        )
        self.bind("")
        file_menu.add_separator()
        file_menu.add_command(
            label="Options",
            command=lambda: [self.popup(), self.reset_board()]
        )
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=quit)
        menu_bar.add_cascade(label="File", menu=file_menu)

    def _create_board_display(self) -> None:
        display_info_frame = tk.Frame(master=self.master_frame, background= "#aab7b8")
        display_info_frame.place(x=0, y=0 , relheight=0.15, relwidth=1)
        display_info_frame.columnconfigure((0,1,2), weight = 1)
        display_info_frame.rowconfigure((0,1,2), weight = 1)

        self.display = tk.Label(
            master = display_info_frame,
            text ="Ready?",
            font = font.Font(size = 20, weight = "bold"),
            background="#aab7b8",
        )
        self.display.grid(row=2, column=0, columnspan=3, sticky="nsew")

        self.player_one_label_display = tk.Label(
            master = display_info_frame,
            text ="Player one?",
            font = font.Font(size = 10),
            background="#aab7b8",
        )
        self.player_one_label_display.grid(row=0, column=0, sticky="nsew")
        self.player_one_score_display = tk.Label(
            master = display_info_frame,
            text = self.player_one_score,
            font = font.Font(size = 10),
            background="#aab7b8",
        )
        self.player_one_score_display.grid(row=1, column=0, sticky="nsew")

        self.player_two_label_display = tk.Label(
            master = display_info_frame,
            text ="Player one?",
            font = font.Font(size = 10),
            background="#aab7b8",
        )
        self.player_two_label_display.grid(row=0, column=2, sticky="nsew")
        self.player_two_score_display = tk.Label(
            master = display_info_frame,
            text = self.player_two_score,
            font = font.Font(size = 10),
            background="#aab7b8",
        )
        self.player_two_score_display.grid(row=1, column=2, sticky="nsew")

    def _create_board_grid(self) -> None:
        grid_frame = tk.Frame(master = self.master_frame, background="#aab7b8")
        grid_frame.place(relx=0, rely=0.15 , relheight=0.85, relwidth=1)
        for row in range(self._game.board_size):
            grid_frame.rowconfigure(row, weight = 1, minsize = 50)
            grid_frame.columnconfigure(row, weight = 1, minsize = 75)
            for col in range(self._game.board_size):
                cell_number = row * self._game.board_size + col + 1
                button = tk.Button(
                    master = grid_frame,
                    text = "",
                    font = font.Font(size = 36, weight = "bold"),
                    bg = "#aed6f1",
                    fg = "black",
                    width = 3,
                    height = 2,
                    activebackground="#c39bd3",
                )
                button.num_label = cell_number
                self._cells[button] = (row, col)
                button.bind("<ButtonPress-1>", self.play)
                button.grid(
                    row = row,
                    column = col,
                    padx = 5,
                    pady = 5,
                    sticky = "nsew"
                )
    
    def play(self, event) -> None:
        update_move_list_check = [item.cpu for item in self._game.players_list]
        #Handle a player's move
        if self._game.current_player.cpu:
            clicked_button = event
        else:
            clicked_button = event.widget
        row, col = self._cells[clicked_button]
        move = Move(row, col, self._game.current_player.label)
        if self._game.is_valid_move(move):
            self._update_button(clicked_button)
            self._game.process_move(move)
            if any(update_move_list_check):#Will only run if there is a cpu player
                if self._game.current_player.cpu:
                    self._game.cpu_moves.append([row, col])
                else:
                    self._game.player_moves.append([row, col])
            if self._game.is_tied():
                self._update_display(msg = "Tied game!", color = "red")
            elif self._game.has_winner():
                self._highlight_cells()
                self._update_display_msg()
                msg = f'"{self.current_player_display_info}" won!'
                if self._game.current_player == self._game.players_list[0]:
                    self.player_one_score = self.player_one_score +1
                    self.player_one_score_display["text"] = self.player_one_score
                elif self._game.current_player == self._game.players_list[1]:
                    self.player_two_score = self.player_two_score +1
                    self.player_two_score_display["text"] = self.player_two_score
                color = self._game.current_player.color
                self._update_display(msg, color)
            else:
                self._game.toggle_player()
                self._update_display_msg()
                msg = f"{self.current_player_display_info}'s turn"
                self._update_display(msg)
                if self._game.current_player.cpu:
                    self._logic.cpu_play()

    def _update_button(self, clicked_btn):
        clicked_btn.config(text=self._game.current_player.label)
        clicked_btn.config(fg=self._game.current_player.color)
    
    def _update_display(self, msg, color="black"):
        self.display["text"] = msg
        self.display["fg"] = color

    def _update_display_msg(self):
        self.current_player_display_info = ""
        if self.vs_cpu_status:
            if self._game.current_player.cpu:
                self.current_player_display_info = "Cpu"
            elif self._game.current_player.cpu == False:
                self.current_player_display_info = self._game.current_player.name
        elif self.vs_cpu_status is False:
            self.current_player_display_info = self._game.current_player.name

    def _update_player_one_info_display(self, msg, color="black"):
        self.player_one_label_display["text"] = msg
        self.player_one_label_display["fg"] = color

    def _update_player_two_info_display(self, msg, color="black"):
        self.player_two_label_display["text"] = msg
        self.player_two_label_display["fg"] = color

    def _highlight_cells(self):
        for button, coordinates in self._cells.items():
            if coordinates in self._game.winner_combo:
                button.config(highlightbackground="red")

    def reset_board(self):
        #Reset the game's board to play again
        self._game.reset_game()
        self._update_display(msg="Ready?")
        self.player_one_score = 0
        self.player_one_score_display["text"] = self.player_one_score
        self.player_two_score = 0
        self.player_two_score_display["text"] = self.player_two_score
        self._update_player_one_info_display("Player one")
        self._update_player_two_info_display("Player two")
        for button in self._cells.keys():
            button.config(highlightbackground="lightblue")
            button.config(text="")
            button.config(fg="black")

    def restart_game(self):
        """Restarts the game keeping the sttings to play again."""
        for row, row_content in enumerate(self._game._current_moves):
            for col, _ in enumerate(row_content):
                row_content[col] = Move(row, col)
        self._game._has_winner = False
        self._game.winner_combo = []
        self._game.cpu_moves = []
        self._game.player_moves = []
        for button in self._cells.keys():
            button.config(highlightbackground="lightblue")
            button.config(text="")
            button.config(fg="black")
        if self.vs_cpu_status:
            if self.vs_cpu_info[0] == 1:
                self._update_display(msg="Player one's turn")
            self._game.set_cpu_player(self.vs_cpu_info[0],self.vs_cpu_info[1])
            self._game.set_players(self._game.players_list)
            self._logic.cpu_play()
        else:
            self._update_display(msg="Player one's turn")
            self._game.set_players(self._game.players_list)
            self._logic.cpu_play()

class TicTacToeGameCpuLogic:
    def __init__(self, game, board):
        self._game = game
        self._board = board

    def block_win_check(self):
        for win_combo in self._game._winning_combos:
            player_count = 0
            cpu_count = 0
            player_moves = [tuple(item) for item in self._game.player_moves]
            cpu_moves = [tuple(item) for item in self._game.cpu_moves]
            if not(bool(set(player_moves) & set(win_combo))):
                for move in win_combo:
                    for cpu_move in self._game.cpu_moves:
                        if list(move) == cpu_move:
                            cpu_count += 1
            elif not bool(set(cpu_moves) & set(win_combo)):
                for move in win_combo:
                    for player_move in self._game.player_moves:
                        if list(move) == player_move:
                            player_count += 1
            if cpu_count == BOARD_SIZE -1:
                self.cpu_winning_move.append(set(win_combo) - set(cpu_moves))
            elif player_count == BOARD_SIZE -1:
                self.player_winning_move.append(set(win_combo) - set(player_moves))

    def cpu_first_move(self) -> int:
        self.corners = self.get_corners()
        self.center = self.get_center()
        self.best_first_move_options = self.get_center()+self.get_corners()
        self.best_first_move_options_list = [list(value) for key, value in self.best_first_move_options]
        if len(self._game.player_moves) ==0:
            [key, value] = random.choice(self.best_first_move_options)
            return key
        elif len(self._game.player_moves) ==1:
            if self._game.player_moves[0] in self.best_first_move_options_list:
                if tuple(self._game.player_moves[0]) == self.center[0][1]:
                    [key, value] = random.choice(self.corners)
                    return key
                elif tuple(self._game.player_moves[0]) is not self.center[0][1]:
                    return self.center[0][0]
            else:
                return self.center[0][0]

    def double_threat_setup(self):
        #This is the logic for the cpu's second and third move which will play into setting up the double threat
        player_moves = [tuple(item) for item in self._game.player_moves]
        cpu_moves = [tuple(item) for item in self._game.cpu_moves]
        best_move_options = [tuple(item) for item in self.best_first_move_options_list]
        best_moves = [item for item in best_move_options if item not in player_moves+cpu_moves]
        available_moves = [[key, value] for key, value in self.best_first_move_options if value in best_moves]
        if len(player_moves)+len(cpu_moves) == 2:
            if player_moves[0] in best_move_options:
                if [value for key,value in available_moves if value == self.center[0][1]]:
                    return self.center[0][0]
                elif self.center[0][1] in player_moves:
                    move = [key for key,value in available_moves if value[0] is not cpu_moves[0][0] and value[1] is not cpu_moves[0][1]]
                    return move[0]
                else:
                    [key, value] = random.choice(available_moves)
                    return key
            else:
                if self.center[0][1] in cpu_moves:
                    move = [key for key,value in available_moves if value[0] is not player_moves[0][0] and value[1] is not player_moves[0][1]]
                    return random.choice(move)
                else:
                    return self.center[0][0]
        elif len(player_moves)+len(cpu_moves) == 3:
            next_cpu_move = []
            #Loop through all the possible win combinations
            for win_combo in self._game._winning_combos:
                #Transform every item in self._game.player_moves/cpu_moves into a tuple so that it matches the win_combo format
                player_moves = [tuple(item) for item in self._game.player_moves]
                cpu_moves = [tuple(item) for item in self._game.cpu_moves]
                #Using set() with the "&" (intersection operator), filter out the win_combos that the player has some progress in
                if not(bool(set(player_moves) & set(win_combo))):
                    if bool(set(cpu_moves) & set(win_combo)):
                        for move in win_combo:
                            for cpu_move in self._game.cpu_moves:
                                if not bool(list(move) == cpu_move):
                                    next_cpu_move.append(move)
            
            next_cpu_move_rng = random.choice(next_cpu_move)
            chosen_move = [key for key, value in available_moves if tuple(value) == next_cpu_move_rng]
            return chosen_move[0]

    def get_corners(self):
        board_size = self._game.board_size
        corner_coords = {(0,0), (0, board_size-1), (board_size-1,0), (board_size-1, board_size-1)}
        return [[button, coord] for button, coord in self._board._cells.items() if coord in corner_coords]

    def get_center(self):
        board_size = self._game.board_size
        center_coord = (board_size // 2, board_size // 2)
        return [[button, coord] for button, coord in self._board._cells.items() if coord == center_coord]

    def cpu_play(self) -> None:
        available_moves = []
        keys, values = list(self._board._cells), list(self._board._cells.values())
        self.player_winning_move = []
        self.cpu_winning_move = []
        self.block_win_check()
        #Logic for choosing where to move
        if self._game.current_player.cpu:
            if self._board.hard_mode_status:
                if len(self.cpu_winning_move) > 0:
                    for key, value in zip(keys, values):
                        if value in self.cpu_winning_move[0]:
                            self._board.play(key)
                elif len(self.player_winning_move) > 0:
                    for key, value in zip(keys, values):
                        if value in self.player_winning_move[0]:
                            self._board.play(key)
                else:
                    if len(self._game.player_moves) + len(self._game.cpu_moves) <= 1:
                        self._board.play(self.cpu_first_move())
                    elif len(self._game.player_moves) + len(self._game.cpu_moves) in range(2, 4):
                        self._board.play(self.double_threat_setup())
                    else:
                        for key in keys:
                            if key.config("text")[4] == "":
                                available_moves.append(key)
                        self._board.play(random.choice(available_moves))
            else:
                for key in keys:
                    if key.config("text")[4] == "":
                        available_moves.append(key)
                self._board.play(random.choice(available_moves))
        available_moves = []

def main():
    """Create game board and run its main loop"""
    game = TicTacToeGame()
    board = TicTacToeBoard(game)
    logic = TicTacToeGameCpuLogic(game, board)
    board._logic = logic
    board.mainloop()

if __name__ == "__main__":
    main()