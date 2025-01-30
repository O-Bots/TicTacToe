import tkinter as tk
from itertools import cycle
from tkinter import font
from typing import NamedTuple
import random

class Player(NamedTuple):
    label: str
    color: str
    cpu: bool

class Move(NamedTuple):
    row: int
    col: int
    label: str = ""

BOARD_SIZE: int = 3
DEFAULT_PLAYERS = (
    Player(label = "X", color = "blue", cpu = False),
    Player(label = "O", color = "green", cpu = False),
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

    def set_players(self, players):
        self._players = cycle(players)
        self.current_player = next(self._players)

    def _setup_board(self) -> None:
        self._current_moves = [
            [Move(row, col) for col in range(self.board_size)]
            for row in range(self.board_size)
        ]
        self._winning_combos = self._get_winning_combos()

    def _get_winning_combos(self):
        rows = [
            [(move.row, move.col) for move in row]
            for row in self._current_moves
        ]
        columns = [list(col) for col in zip(*rows)]
        first_diagonal = [row[i] for i, row in enumerate(rows)]
        second_diagonal = [col[j] for j, col in enumerate(reversed(columns))]
        return rows + columns + [first_diagonal, second_diagonal]
    
    def is_valid_move(self, move):
        """Return True if move is valid, and false otherwise"""
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
        self.winner_combo = []
        self.cpu_moves = []
        self.player_moves = []
        self.current_player = DEFAULT_PLAYERS[0]

    def set_cpu_player(self, player_index: int, new_cpu_value: bool):
        old_player = self.players_list[player_index]
        updated_player = old_player._replace(cpu=new_cpu_value)
        self.players_list[player_index] = updated_player
        self._players = cycle(self.players_list)



class TicTacToeBoard(tk.Tk):
    def __init__(self, game) -> None:
        super().__init__()
        self.title("Tic-Tac-Toe Game")
        self._cells = {}
        self._game = game
        self.eval("tk::PlaceWindow . center")
        self.popup()
        self._create_menu()
        self._create_board_display()
        self._create_board_grid()
        

    def popup(self):
        self.cpu_mode_option = tk.IntVar()
        self.easy_mode_option = tk.IntVar()
        self.twitch_mode_option = tk.IntVar()
        self.first_player_mode_option = tk.IntVar()
        self.popup_window = tk.Toplevel()
        self.eval(f"tk::PlaceWindow {str(self.popup_window)} center")
        self.popup_window.title("Popup")
        self.popup_window.attributes("-topmost", True)
        self.popup_window.bind("<FocusOut>", lambda event: self.popup_window.focus_force())
        self.popup_window.protocol('WM_DELETE_WINDOW', 'break')
        self.popup_window.first_player_check = tk.Checkbutton(
            self.popup_window, 
            text="Play First?",
            variable=self.first_player_mode_option,
            onvalue=1,
            offvalue=0,
            font=("helvetica", 13)).pack(pady=(5),padx=(20))
        self.popup_window.cpu_check = tk.Checkbutton(
            self.popup_window, 
            text="Play VS the CPU",
            variable=self.cpu_mode_option,
            onvalue=1,
            offvalue=0,
            font=("helvetica", 13)).pack(pady=(5),padx=(20))
        self.popup_window.easy_mode_check = tk.Checkbutton(
            self.popup_window, 
            text="Easy Mode",
            variable=self.easy_mode_option,
            onvalue=1, 
            offvalue=0,
            font=("helvetica", 13)).pack(pady=(5),padx=(20))
        self.popup_window.twitch_check = tk.Checkbutton(
            self.popup_window, 
            text="Twitch Plays",
            variable=self.twitch_mode_option,
            onvalue=1, 
            offvalue=0,
            font=("helvetica", 13)).pack(pady=(5),padx=(20))
        self.popup_window.confirm_button = tk.Button(
            self.popup_window, 
            text="Confirm", 
            command=self.confirm_button,
            font=("helvetica", 13)).pack(side="bottom", padx=10,pady=10)
        self.attributes("-disabled", True)
    

    def confirm_button(self):

        self.attributes("-disabled", False)
        self.popup_window.destroy()
        if self.easy_mode_option.get() == 1:
            self._game.hard_mode = False
        if self.cpu_mode_option.get() == 1:
            self._game.set_cpu_player(1, True)
        self._game.set_players(self._game.players_list)
        self.cpu_play()

    def _create_menu(self):
        menu_bar = tk.Menu(master=self)
        self.config(menu=menu_bar)
        file_menu = tk.Menu(master=menu_bar)
        file_menu.add_command(
            label="Play Again",
            command=self.reset_board
        )
        file_menu.add_command(
            label="Options",
            command=lambda: [self.popup(), self.reset_board()]
        )
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=quit)
        menu_bar.add_cascade(label="File", menu=file_menu)

    def _create_board_display(self) -> None:
        display_frame = tk.Frame(
            master = self,
            background="#aab7b8",
        )
        display_frame.pack(fill=tk.X)
        self.display = tk.Label(
            master = display_frame,
            text ="Ready?",
            font = font.Font(size = 28, weight = "bold"),
            background="#aab7b8",
        )
        self.display.pack()

    def _create_board_grid(self) -> None:
        grid_frame = tk.Frame(
            master = self,
            background="#aab7b8",
        )
        grid_frame.pack()
        for row in range(self._game.board_size):
            self.rowconfigure(row, weight = 1, minsize = 50)
            self.columnconfigure(row, weight = 1, minsize = 75)
            for col in range(self._game.board_size):
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
                self._cells[button] = (row, col)
                button.bind("<ButtonPress-1>", self.play)
                button.grid(
                    row = row,
                    column = col,
                    padx = 5,
                    pady = 5,
                    sticky = "nsew"
                )

    def cpu_play(self) -> None:
        available_moves = []
        keys, values = list(self._cells), list(self._cells.values())
        player_winning_move = []
        cpu_winning_move = []
        #Blocking player, Winning move logic
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
                cpu_winning_move.append(set(win_combo) - set(cpu_moves))
            elif player_count == BOARD_SIZE -1:
                player_winning_move.append(set(win_combo) - set(player_moves))

        #Logic for choosing where to move
        if self._game.current_player.cpu:
            if self._game.hard_mode:
                if len(cpu_winning_move) > 0:
                    for key, value in zip(keys, values):
                        if value in cpu_winning_move[0]:
                            self.play(key)
                elif len(player_winning_move) > 0:
                    for key, value in zip(keys, values):
                        if value in player_winning_move[0]:
                            self.play(key)
                else:
                    for key in keys:
                        if key.config("text")[4] == "":
                            available_moves.append(key)
                    self.play(random.choice(available_moves))
            else:
                for key in keys:
                    if key.config("text")[4] == "":
                        available_moves.append(key)
                self.play(random.choice(available_moves))
        available_moves = []
    
    def play(self, event) -> None:
        #Handle a player's move
        if self._game.current_player.cpu:
            clicked_button = event
        else:
            clicked_button = event.widget
        row, col = self._cells[clicked_button]
        move = Move(row, col, self._game.current_player.label)
        if self._game.is_valid_move(move):
            if any(DEFAULT_PLAYERS):#Will only run if there is a cpu player
                if self._game.current_player.cpu:
                    self._game.cpu_moves.append([row, col])
                else:
                    self._game.player_moves.append([row, col])
            self._update_button(clicked_button)
            self._game.process_move(move)
            if self._game.is_tied():
                self._update_display(msg = "Tied game!", color = "red")
            elif self._game.has_winner():
                self._highlight_cells()
                msg = f'Player "{self._game.current_player.label}" won!'
                color = self._game.current_player.color
                self._update_display(msg, color)
            else:
                self._game.toggle_player()
                msg = f"{self._game.current_player.label}'s turn"
                self._update_display(msg)
                if self._game.current_player.cpu:
                    self.cpu_play()


    def _update_button(self, clicked_btn):
        clicked_btn.config(text=self._game.current_player.label)
        clicked_btn.config(fg=self._game.current_player.color)
    
    def _update_display(self, msg, color="black"):
        self.display["text"] = msg
        self.display["fg"] = color

    def _highlight_cells(self):
        for button, coordinates in self._cells.items():
            if coordinates in self._game.winner_combo:
                button.config(highlightbackground="red")

    def reset_board(self):
        #Reset the game's board to play again
        self._game.reset_game()
        self._update_display(msg="Ready?")
        for button in self._cells.keys():
            button.config(highlightbackground="lightblue")
            button.config(text="")
            button.config(fg="black")

def main():
    """Create game board and run its main loop"""
    game = TicTacToeGame()
    board = TicTacToeBoard(game)
    board.mainloop()

if __name__ == "__main__":
    main()