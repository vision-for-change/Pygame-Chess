"""
TITLE: Pygame Chess Game ( En Passant )

PROGRAM DESCRIPTION:
This program is a fully functional two-player chess game created using Python and the Pygame library. 
The purpose of the program is to simulate a real game of chess while providing an interactive graphical user interface for players.

The game begins with a title screen where both players enter their names before starting the match. Once the game starts, players take turns selecting and moving chess pieces according to standard chess rules. The program validates all moves to ensure they are legal before allowing them to be made.

Features of the program include:
- Standard movement rules for all chess pieces (Pawn, Rook, Knight, Bishop, Queen, and King)
-  Move validation to prevent illegal moves
-  Check detection
-  Castling on both the kingside and queenside
-  Automatic pawn promotion to a Queen
- Turn management between White and Black players
- Individual timers for each player
- Visual highlights for selected pieces and valid moves
- Chessboard graphics and piece images loaded from external files
- Win conditions based on king capture or timer expiration

The program utilizes multiple functions and data structures to manage game logic, piece movement, board rendering, timer updates, and user interaction.

AUTHOR:
Nimansh Chauhan

DATE:
22 June 2026

LINES OF CODE: SOURCE

Lines 109-120
SOURCE: Python OS Library Documentation
https://docs.python.org/3/library/os.html

Lines 95-118
SOURCE: Pygame Image Documentation
https://www.pygame.org/docs/ref/image.html

Lines 118, 146 
SOURCE: Pygame Transform Documentation
https://www.pygame.org/docs/ref/transform.html

Lines 101-105, 531-564
SOURCE: Python Dictionaries Documentation
https://docs.python.org/3/tutorial/datastructures.html#dictionaries

Lines involving use of any(), 923-924
SOURCE: Python Built-in Functions Documentation
https://docs.python.org/3/library/functions.html#any

General Python syntax and built-in functions
SOURCE: Python Documentation
https://docs.python.org/3/

General Pygame game development concepts
SOURCE: Pygame Documentation
https://www.pygame.org/docs/

"""

# imported two libraries:
# pygame is used to create the game window, graphics, input handling, and game loop
# os is used to access file paths for loading images from folders
import pygame
import os


# initializes all pygame modules like graphics, sound, fonts, and input
pygame.init()


# window size has the board plus the sidebar and bottom ui panel
BOARD_HEIGHT = 640
INFO_BAR_HEIGHT = 80
WIDTH, HEIGHT = 800, BOARD_HEIGHT + INFO_BAR_HEIGHT

# size of each chess square
SQUARE_SIZE = 80

# rgb color values for the chessboard and highlights
WHITE = (238, 238, 210)   # light squares
GREEN = (118, 150, 86)    # dark squares
YELLOW = (255, 255, 0)    # move highlight


# creates the game window
screen = pygame.display.set_mode((WIDTH, HEIGHT))

# sets title at top of window
pygame.display.set_caption("Chess Game")


# load piece images from the assets folder and scale them to square size

def load_images():
    # load and resize every chess piece image
    # create dictionary to store each loaded piece image
    pieces = {}

    # map piece codes to filenames so images can be loaded by code
    piece_files = {
        "wP": "White_Pawn.png", "wR": "White_Rook.png", "wH": "White_Horse.png",
        "wB": "White_Bishop.png", "wQ": "White_Queen.png", "wK": "White_King.png",
        "bP": "Black_Pawn.png", "bR": "Black_Rook.png", "bH": "Black_Horse.png",
        "bB": "Black_Bishop.png", "bQ": "Black_Queen.png", "bK": "Black_King.png"
    }

    # load each image file and store it in pieces dictionary
    for key, filename in piece_files.items():

        # build path to the image file inside assets
        path = os.path.join("assets", filename)

        # load image from disk into pygame surface
        img = pygame.image.load(path)

        # scale image to fit a board square and store it
        pieces[key] = pygame.transform.scale(img, (SQUARE_SIZE, SQUARE_SIZE))

    return pieces


# store full and scaled piece images for board drawing and capture display
IMAGES = load_images()
SMALL_IMAGES = {key: pygame.transform.scale(img, (32, 32)) for key, img in IMAGES.items()}

# draw a decorative background with large translucent pieces for menu screens
def draw_screen_background():
    # paint the menu background before adding decorative pieces
    screen.fill((238, 238, 210))
    bg_pieces = ["wK", "bK", "wQ", "bQ", "wR", "bR", "wB", "bB"]
    positions = [
        (WIDTH * 0.08, HEIGHT * 0.08),
        (WIDTH * 0.58, HEIGHT * 0.08),
        (WIDTH * 0.18, HEIGHT * 0.30),
        (WIDTH * 0.68, HEIGHT * 0.30),
        (WIDTH * 0.05, HEIGHT * 0.62),
        (WIDTH * 0.62, HEIGHT * 0.58),
        (WIDTH * 0.30, HEIGHT * 0.72),
        (WIDTH * 0.76, HEIGHT * 0.72)
    ]
    sizes = [140, 140, 120, 120, 100, 100, 90, 90]

    # place each large piece image at a position with transparency
    for key, pos, size in zip(bg_pieces, positions, sizes):
        img = pygame.transform.smoothscale(IMAGES[key], (size, size))
        img.set_alpha(60)
        screen.blit(img, pos)

    # draw a semi-transparent overlay to soften the background
    overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    overlay.fill((238, 238, 210, 180))
    screen.blit(overlay, (0, 0))

# 8x8 chess board represented as a 2d list
# each element is a string:
# "wp" means white pawn, "br" means black rook, and "--" means empty square
board = [
    ["bR", "bH", "bB", "bQ", "bK", "bB", "bH", "bR"],
    ["bP", "bP", "bP", "bP", "bP", "bP", "bP", "bP"],
    ["--", "--", "--", "--", "--", "--", "--", "--"],
    ["--", "--", "--", "--", "--", "--", "--", "--"],
    ["--", "--", "--", "--", "--", "--", "--", "--"],
    ["--", "--", "--", "--", "--", "--", "--", "--"],
    ["wP", "wP", "wP", "wP", "wP", "wP", "wP", "wP"],
    ["wR", "wH", "wB", "wQ", "wK", "wB", "wH", "wR"]
]

# track captured pieces for each player
white_captured = []
black_captured = []



def board_to_screen(row, col, flipped):
    # convert a board square into screen pixels
    # flip coordinates when it is black's turn
    if flipped:
        row = 7 - row
        col = 7 - col
    return col * SQUARE_SIZE, row * SQUARE_SIZE


def screen_to_board(pos, flipped):
    # convert a mouse position into a board square
    col = pos[0] // SQUARE_SIZE
    row = pos[1] // SQUARE_SIZE
    # flip coordinates back when the board is shown from black's side
    if flipped:
        row = 7 - row
        col = 7 - col
    return row, col


# draw the board squares with alternating light and dark colors
def draw_board(flipped=False):
    # draw each row of the chessboard
    for r in range(8):
        # draw each square in the current row
        for c in range(8):
            # pick the light or dark square color
            if (r + c) % 2 == 0:
                color = WHITE
            else:
                color = GREEN
            x, y = board_to_screen(r, c, flipped)
            pygame.draw.rect(screen, color, (x, y, SQUARE_SIZE, SQUARE_SIZE))


def draw_pieces(flipped=False):
    # draw every visible piece on the board
    # draw all pieces currently stored on the board
    for r in range(8):
        # check each square in this row for a piece
        for c in range(8):
            piece = board[r][c]
            # only draw squares that contain a piece
            if piece != "--":
                x, y = board_to_screen(r, c, flipped)
                screen.blit(IMAGES[piece], (x, y))


def get_valid_moves(row, col):
    # find basic moves for a piece without checking king safety
    # compute possible moves for a piece ignoring checks
    moves = []
    piece = board[row][col]

    knight_moves = [
        (-2, -1), (-2, 1),
        (-1, -2), (-1, 2),
        (1, -2), (1, 2),
        (2, -1), (2, 1)
    ]

    # handle knight movement
    if piece in ["wH", "bH"]:
        # test each l-shaped knight jump
        for dr, dc in knight_moves:
            r, c = row + dr, col + dc
            # keep moves inside the board
            if 0 <= r < 8 and 0 <= c < 8:
                # white knights can move to empty squares or black pieces
                if piece == "wH":
                    if board[r][c] == "--" or board[r][c][0] == "b":
                        moves.append((r, c))
                # black knights can move to empty squares or white pieces
                else:
                    if board[r][c] == "--" or board[r][c][0] == "w":
                        moves.append((r, c))

    # handle white pawn movement
    elif piece == "wP":

        # move forward 1 square
        if row > 0 and board[row - 1][col] == "--":
            moves.append((row - 1, col))

            # double move from starting position
            if row == 6 and board[row - 2][col] == "--":
                moves.append((row - 2, col))

        # capture diagonally left
        if row > 0 and col > 0 and board[row - 1][col - 1] != "--":
            if board[row - 1][col - 1][0] == "b":
                moves.append((row - 1, col - 1))

        # capture diagonally right
        if row > 0 and col < 7 and board[row - 1][col + 1] != "--":
            if board[row - 1][col + 1][0] == "b":
                moves.append((row - 1, col + 1))


    # handle black pawn movement in the opposite direction
    elif piece == "bP":

        # move forward
        if row < 7 and board[row + 1][col] == "--":
            moves.append((row + 1, col))

            # double move from start
            if row == 1 and board[row + 2][col] == "--":
                moves.append((row + 2, col))

        # capture left
        if row < 7 and col > 0:
            if board[row + 1][col - 1] != "--":
                if board[row + 1][col - 1][0] == "w":
                    moves.append((row + 1, col - 1))

        # capture right
        if row < 7 and col < 7:
            if board[row + 1][col + 1] != "--":
                if board[row + 1][col + 1][0] == "w":
                    moves.append((row + 1, col + 1))
                    

    # handle rook movement
    elif piece in ["wR", "bR"]:

        # directions: vertical + horizontal
        directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]

        for dr, dc in directions:

            r, c = row + dr, col + dc

            # keep moving until blocked
            while 0 <= r < 8 and 0 <= c < 8:

                if board[r][c] == "--":
                    moves.append((r, c))

                elif piece == "wR" and board[r][c][0] == "b":
                    moves.append((r, c))  # capture enemy piece
                    break

                elif piece == "bR" and board[r][c][0] == "w":
                    moves.append((r, c))  # capture enemy piece
                    break

                else:
                    break  # same color piece blocks movement
                r += dr
                c += dc

    # handle bishop movement
    elif piece in ["wB", "bB"]:

        # diagonal directions
        directions = [(-1, -1), (-1, 1), (1, -1), (1, 1)]

        for dr, dc in directions:

            r, c = row + dr, col + dc

            while 0 <= r < 8 and 0 <= c < 8:

                if board[r][c] == "--":
                    moves.append((r, c))

                elif piece == "wB" and board[r][c][0] == "b":
                    moves.append((r, c))
                    break

                elif piece == "bB" and board[r][c][0] == "w":
                    moves.append((r, c))
                    break

                else:
                    break

                r += dr
                c += dc


    # handle queen movement as rook and bishop movement combined
    elif piece in ["wQ", "bQ"]:

        # rook + bishop combined directions
        directions = [
            (-1, 0), (1, 0), (0, -1), (0, 1),
            (-1, -1), (-1, 1), (1, -1), (1, 1)
        ]

        for dr, dc in directions:

            r, c = row + dr, col + dc

            while 0 <= r < 8 and 0 <= c < 8:

                if board[r][c] == "--":
                    moves.append((r, c))

                elif piece == "wQ" and board[r][c][0] == "b":
                    moves.append((r, c))
                    break

                elif piece == "bQ" and board[r][c][0] == "w":
                    moves.append((r, c))
                    break

                else:
                    break

                r += dr
                c += dc


    # handle king movement
    elif piece in ["wK", "bK"]:

        # one-square movement in all directions
        directions = [
            (-1, 0), (1, 0), (0, -1), (0, 1),
            (-1, -1), (-1, 1), (1, -1), (1, 1)
        ]

        for dr, dc in directions:

            r, c = row + dr, col + dc

            if 0 <= r < 8 and 0 <= c < 8:

                if piece == "wK":
                    if board[r][c] == "--" or board[r][c][0] == "b":
                        moves.append((r, c))

                else:
                    if board[r][c] == "--" or board[r][c][0] == "w":
                        moves.append((r, c))

        # check castling options
        if col == 4:
            # white king can castle only from its starting row
            if piece == "wK" and row == 7:
                if board[7][7] == "wR" and board[7][5] == "--" and board[7][6] == "--":
                    moves.append((7, 6))
                if board[7][0] == "wR" and board[7][1] == "--" and board[7][2] == "--" and board[7][3] == "--":
                    moves.append((7, 2))
            # black king can castle only from its starting row
            elif piece == "bK" and row == 0:
                if board[0][7] == "bR" and board[0][5] == "--" and board[0][6] == "--":
                    moves.append((0, 6))
                if board[0][0] == "bR" and board[0][1] == "--" and board[0][2] == "--" and board[0][3] == "--":
                    moves.append((0, 2))

    return moves


def king_present():
    # check that both kings are still on the board
    white_king = False
    black_king = False

    # scan each board row for kings
    for row in board:
        # check every square in the current row
        for square in row:
            # remember when the white king is found
            if square == "wK":
                white_king = True
            # remember when the black king is found
            elif square == "bK":
                black_king = True

    return white_king and black_king

def pawn_promotion(row, col):
    # promote a pawn if it reaches the far side
    piece = board[row][col]
    # white pawns promote on the top row
    if piece == "wP" and row == 0:
        board[row][col] = "wQ"  # promote to queen
    # black pawns promote on the bottom row
    elif piece == "bP" and row == 7:
        board[row][col] = "bQ"  # promote to queen


def castling(row, col):
    # move the king and rook for castling if the board is set up for it
    # handle white castling from the starting king file
    if board[row][col] == "wK" and col == 4:
        # kingside castling
        if board[row][7] == "wR" and board[row][5] == "--" and board[row][6] == "--":
            board[row][6] = "wK"
            board[row][5] = "wR"
            board[row][4] = "--"
            board[row][7] = "--"
        # queenside castling
        elif board[row][0] == "wR" and board[row][1] == "--" and board[row][2] == "--" and board[row][3] == "--":
            board[row][2] = "wK"
            board[row][3] = "wR"
            board[row][4] = "--"
            board[row][0] = "--"
    # handle black castling from the starting king file
    elif board[row][col] == "bK" and col == 4:
        # kingside castling
        if board[row][7] == "bR" and board[row][5] == "--" and board[row][6] == "--":
            board[row][6] = "bK"
            board[row][5] = "bR"
            board[row][4] = "--"
            board[row][7] = "--"
        # queenside castling
        elif board[row][0] == "bR" and board[row][1] == "--" and board[row][2] == "--" and board[row][3] == "--":
            board[row][2] = "bK"
            board[row][3] = "bR"
            board[row][4] = "--"
            board[row][0] = "--"
    return board[row][col] in ["wK", "bK"]  


def format_time(seconds):
    # turn seconds into a mm:ss clock label
    minutes = int(seconds) // 60
    sec = int(seconds) % 60
    return f"{minutes:02d}:{sec:02d}"


def is_square_attacked(target_row, target_col, by_player):
    # check if any piece from one player can reach a target square
    # scan every row of the board
    for r in range(8):
        # scan every square in the row
        for c in range(8):
            piece = board[r][c]
            # only test pieces owned by the attacking player
            if piece != "--" and piece[0] == by_player:
                moves = get_valid_moves(r, c)
                # the square is attacked if it appears in that piece's moves
                if (target_row, target_col) in moves:
                    return True
    return False



def is_in_check(player):
    # find the player's king and test if it is attacked
    king_code = player + "K"
    # scan each row for the king
    for r in range(8):
        # scan each square in the current row
        for c in range(8):
            # once the king is found, check attacks from the other player
            if board[r][c] == king_code:
                opponent = "b" if player == "w" else "w"
                return is_square_attacked(r, c, opponent)
    return False


def _simulate_move(sr, sc, tr, tc):
    # temporarily make a move so legal move checks can test the position
    saved = {}
    saved['from'] = (sr, sc, board[sr][sc])
    saved['to'] = (tr, tc, board[tr][tc])
    piece = board[sr][sc]

    board[tr][tc] = piece
    board[sr][sc] = "--"

    # handle castling rook in simulation
    if piece in ["wK", "bK"] and abs(tc - sc) == 2:
        # kingside castling moves the rook from the right corner
        if tc > sc:
            saved['rook'] = (tr, 7, board[tr][7])
            saved['rook_target'] = (tr, 5)
            board[tr][5] = board[tr][7]
            board[tr][7] = "--"
        # queenside castling moves the rook from the left corner
        else:
            saved['rook'] = (tr, 0, board[tr][0])
            saved['rook_target'] = (tr, 3)
            board[tr][3] = board[tr][0]
            board[tr][0] = "--"

    # promotion is also simulated because it can affect check
    if board[tr][tc] == "wP" and tr == 0:
        saved['promo'] = True
        board[tr][tc] = "wQ"
    elif board[tr][tc] == "bP" and tr == 7:
        saved['promo'] = True
        board[tr][tc] = "bQ"

    return saved


def _undo_simulation(saved):
    # restore the board after a temporary move
    sr, sc, from_piece = saved['from']
    tr, tc, to_piece = saved['to']
    board[sr][sc] = from_piece
    board[tr][tc] = to_piece
    # restore rook state if the simulated move was castling
    if 'rook' in saved:
        rr, rc, rpiece = saved['rook']
        board[rr][rc] = rpiece
        # clear the rook's temporary castling destination if it was moved
        if 'rook_target' in saved:
            trr, trc = saved['rook_target']
            board[trr][trc] = "--"


def get_legal_moves(row, col):
    # filter basic moves so they do not leave the king in check
    piece = board[row][col]
    # empty squares have no legal moves
    if piece == "--":
        return []
    owner = piece[0]
    possible = get_valid_moves(row, col)
    legal = []
    # test each possible move with a temporary board state
    for tr, tc in possible:
        saved = _simulate_move(row, col, tr, tc)
        still_in_check = is_in_check(owner)
        _undo_simulation(saved)
        # keep only moves that leave the owner safe
        if not still_in_check:
            legal.append((tr, tc))
    return legal


def has_any_legal_moves(player):
    # check whether a player has at least one move available
    # scan each row for that player's pieces
    for r in range(8):
        # scan each square in the current row
        for c in range(8):
            # only pieces owned by this player can create legal moves
            if board[r][c] != "--" and board[r][c][0] == player:
                # one legal move is enough to prove the game can continue
                if get_legal_moves(r, c):
                    return True
    return False


def main(player_names):
    # run the main chess game loop after setup is finished
    running = True
    selected_sq = None
    valid_moves = []
    current_player = "w"
    clock = pygame.time.Clock()
    white_time = 10 * 60.0
    black_time = 10 * 60.0
    king_warning = False
    king_warning_time = 0
    king_warning_duration = 1500  # ms

    # keep running frames until the game ends or the window closes
    while running:
        dt = clock.tick(60) / 1000.0
        # subtract time from the player whose turn it is
        if current_player == "w":
            white_time -= dt
            # stop the game when white runs out of time
            if white_time <= 0:
                white_time = 0
                timer_screen()
                running = False
        # subtract time from black on black's turn
        else:
            black_time -= dt
            # stop the game when black runs out of time
            if black_time <= 0:
                black_time = 0
                timer_screen()
                running = False

        flipped = (current_player == "b")

        # check for checkmate: player is in check and has no legal moves
        if is_in_check(current_player) and not has_any_legal_moves(current_player):
            white_name, black_name = player_names if player_names else ("White", "Black")
            winner = black_name if current_player == "w" else white_name
            lose_screen(player_names, winner_name=winner)
            running = False
            break

        # process every pygame event from this frame
        for event in pygame.event.get():

            # exit game
            if event.type == pygame.QUIT:
                running = False

            # mouse click event
            elif event.type == pygame.MOUSEBUTTONDOWN:

                pos = pygame.mouse.get_pos()
                # ignore clicks outside the playable board
                if pos[0] >= SQUARE_SIZE * 8 or pos[1] >= BOARD_HEIGHT:
                    continue

                # convert pixel position to board coordinates
                row, col = screen_to_board(pos, flipped)

                # select a piece when nothing is selected yet
                if selected_sq is None:

                    # only the current player's pieces can be selected
                    if board[row][col] != "--" and board[row][col][0] == current_player:
                        legal = get_legal_moves(row, col)
                        # if king is in check, disallow selecting a piece that cannot resolve check
                        if is_in_check(current_player) and not legal:
                            king_warning = True
                            king_warning_time = pygame.time.get_ticks()
                        # save the selected piece and its legal moves
                        else:
                            selected_sq = (row, col)
                            valid_moves = legal

                # move a piece or switch selection after one is already selected
                else:
                    # clicking another friendly piece switches selection
                    if board[row][col] != "--" and board[row][col][0] == current_player:
                        legal = get_legal_moves(row, col)
                        # warn if this piece cannot help while the king is checked
                        if is_in_check(current_player) and not legal:
                            king_warning = True
                            king_warning_time = pygame.time.get_ticks()
                        # update selected piece and its move list
                        else:
                            selected_sq = (row, col)
                            valid_moves = legal
                    # clicking an empty square or enemy piece attempts a move
                    else:
                        sr, sc = selected_sq
                        piece = board[sr][sc]

                        # check if move is valid
                        if (row, col) in valid_moves:
                            target = board[row][col]
                            # record captured pieces for the sidebar
                            if target != "--":
                                # black captured a white piece
                                if target[0] == "w":
                                    black_captured.append(target)
                                # white captured a black piece
                                else:
                                    white_captured.append(target)

                            # move piece and handle castling
                            if piece in ["wK", "bK"] and sc == 4 and abs(col - sc) == 2:
                                board[row][col] = piece
                                board[sr][sc] = "--"
                                # move rook for kingside castling
                                if col == 6:
                                    board[row][5] = board[row][7]
                                    board[row][7] = "--"
                                # move rook for queenside castling
                                elif col == 2:
                                    board[row][3] = board[row][0]
                                    board[row][0] = "--"
                            # normal moves just move the selected piece
                            else:
                                board[row][col] = piece
                                board[sr][sc] = "--"

                            pawn_promotion(row, col)

                            # end the game if a king was captured
                            if not king_present():
                                lose_screen(player_names)
                                running = False
                            # otherwise switch turns
                            else:
                                current_player = "b" if current_player == "w" else "w"

                        # clear selection after a move attempt
                        selected_sq = None
                        valid_moves = []

        # draw whole background and board
        screen.fill((238, 238, 210))
        draw_board(flipped)

        # highlight valid moves
        for r, c in valid_moves:
            x, y = board_to_screen(r, c, flipped)
            pygame.draw.rect(
                screen,
                YELLOW,
                (x, y, SQUARE_SIZE, SQUARE_SIZE)
            )

        # highlight selected square
        if selected_sq:
            x, y = board_to_screen(selected_sq[0], selected_sq[1], flipped)
            pygame.draw.rect(
                screen,
                (255, 0, 0),
                (x, y, SQUARE_SIZE, SQUARE_SIZE),
                3
            )

        # clear king warning after duration
        if king_warning and pygame.time.get_ticks() - king_warning_time > king_warning_duration:
            king_warning = False

        # if warning is active, draw current player's king in red
        if king_warning:
            king_code = current_player + "K"
            for kr in range(8):
                for kc in range(8):
                    if board[kr][kc] == king_code:
                        kx, ky = board_to_screen(kr, kc, flipped)
                        pygame.draw.rect(screen, (255, 0, 0), (kx, ky, SQUARE_SIZE, SQUARE_SIZE), 6)
                        break
                else:
                    continue
                break

        # draw pieces on top
        draw_pieces(flipped)

        draw_bottom_ui(player_names, current_player, white_time, black_time)
        pieces_taken(current_player, white_time, black_time)

        # update screen
        pygame.display.flip()

    pygame.quit()




def display_menu():
    # show the first screen with the title and start button

    font_title = pygame.font.Font(None, 72)
    font_button = pygame.font.Font(None, 48)

    title_text = font_title.render("En Passant", True, (0, 0, 0))
    start_text = font_button.render("Start", True, (255, 255, 255))

    button_rect = pygame.Rect(WIDTH // 2 - 75, HEIGHT // 2, 150, 60)

    # keep the menu open until start or close is clicked
    while True:

        # handle menu input events
        for event in pygame.event.get():

            # close the app from the menu
            if event.type == pygame.QUIT:
                return False

            # start the game when the start button is clicked
            if event.type == pygame.MOUSEBUTTONDOWN:
                if button_rect.collidepoint(event.pos):
                    return True

        # background image made from piece assets
        draw_screen_background()

        # title text
        screen.blit(title_text, (WIDTH // 2 - title_text.get_width() // 2, HEIGHT * 0.18))

        # start button
        pygame.draw.rect(screen, (118, 150, 86), button_rect)
        screen.blit(start_text, (button_rect.x + button_rect.width // 2 - start_text.get_width() // 2,
                                 button_rect.y + button_rect.height // 2 - start_text.get_height() // 2))

        pygame.display.flip()

def input_screen():
    # collect both player names before starting the match
    font = pygame.font.Font(None, 48)
    small = pygame.font.Font(None, 36)

    white_name = ""
    black_name = ""
    active = "white"

    prompt = font.render("Enter Player Names", True, (0, 0, 0))

    # keep accepting keyboard input until both names are entered
    while True:
        # read each keyboard or window event
        for event in pygame.event.get():
            # closing the window cancels name entry
            if event.type == pygame.QUIT:
                return None, None
            # handle typed keys for the active name field
            if event.type == pygame.KEYDOWN:
                # tab switches between white and black name fields
                if event.key == pygame.K_TAB:
                    active = "black" if active == "white" else "white"
                # enter confirms when both names have text
                elif event.key == pygame.K_RETURN:
                    if white_name.strip() and black_name.strip():
                        return white_name.strip(), black_name.strip()
                # backspace removes the last character from the active field
                elif event.key == pygame.K_BACKSPACE:
                    if active == "white":
                        white_name = white_name[:-1]
                    else:
                        black_name = black_name[:-1]
                # normal printable keys are added to the active field
                else:
                    char = event.unicode
                    if char.isprintable():
                        # add typed characters to white's name
                        if active == "white":
                            white_name += char
                        # add typed characters to black's name
                        else:
                            black_name += char

        # redraw the input screen each frame
        screen.fill((238, 238, 210))
        screen.blit(prompt, (WIDTH // 2 - prompt.get_width() // 2, 80))

        w_label = small.render("White:", True, (0, 0, 0))
        b_label = small.render("Black:", True, (0, 0, 0))

        w_text = small.render(white_name + ("_" if active == "white" else ""), True, (0, 0, 0))
        b_text = small.render(black_name + ("_" if active == "black" else ""), True, (0, 0, 0))

        screen.blit(w_label, (WIDTH // 2 - 200, 180))
        screen.blit(w_text, (WIDTH // 2 - 120, 180))
        screen.blit(b_label, (WIDTH // 2 - 200, 240))
        screen.blit(b_text, (WIDTH // 2 - 120, 240))

        hint = small.render("TAB to switch, ENTER to confirm", True, (0, 0, 0))
        screen.blit(hint, (WIDTH // 2 - hint.get_width() // 2, 320))

        pygame.display.flip()

def lose_screen(player_names, winner_name=None):
    # show the winner screen after checkmate, capture, or timeout
    # player names are stored as white name and black name
    white_name, black_name = player_names
    font = pygame.font.Font(None, 72)
    small = pygame.font.Font(None, 36)

    # determine winner: explicit winner_name beats board inspection
    if winner_name:
        winner = winner_name
    else:
        # determine which king is missing
        w_present = any("wK" in row for row in board)
        b_present = any("bK" in row for row in board)

        # black wins if only white's king is gone
        if not w_present and b_present:
            winner = black_name if black_name else "Black"
        # white wins if only black's king is gone
        elif not b_present and w_present:
            winner = white_name if white_name else "White"
        # fallback message if neither player clearly won
        else:
            winner = "No one"

    text = font.render(f"{winner} wins!", True, (255, 0, 0))

    # keep the winner screen up until the window is closed
    while True:
        # handle close events on the winner screen
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return

        draw_screen_background()
        screen.blit(text, (WIDTH // 2 - text.get_width() // 2, HEIGHT * 0.40 - text.get_height() // 2))
        info = small.render("Close window to exit", True, (0, 0, 0))
        screen.blit(info, (WIDTH // 2 - info.get_width() // 2, HEIGHT * 0.55 - info.get_height() // 2))
        pygame.display.flip()

def pieces_taken(current_player, white_time, black_time):
    # draw the captured pieces sidebar
    rect = pygame.Rect(WIDTH - 150, 10, 140, BOARD_HEIGHT - 20)
    pygame.draw.rect(screen, (255, 255, 255), rect)
    pygame.draw.rect(screen, (0, 0, 0), rect, 2)

    mid_y = rect.y + rect.height // 2
    pygame.draw.line(screen, (0, 0, 0), (rect.x, mid_y), (rect.right, mid_y), 2)

    small = pygame.font.Font(None, 20)
    title_white = small.render("White captures", True, (0, 0, 0))
    title_black = small.render("Black captures", True, (0, 0, 0))
    screen.blit(title_white, (rect.x + 5, rect.y + 5))
    screen.blit(title_black, (rect.x + 5, mid_y + 5))

    def draw_capture_list(piece_list, start_x, start_y):
        # draw one capture list inside the sidebar
        # show none when this player has no captures yet
        if not piece_list:
            none_text = small.render("None", True, (0, 0, 0))
            screen.blit(none_text, (start_x, start_y))
            return

        x = start_x
        y = start_y
        # place each captured piece image in rows
        for piece in piece_list:
            image = SMALL_IMAGES.get(piece)
            # draw the small image when it exists
            if image:
                screen.blit(image, (x, y))
                x += image.get_width() + 4
                # wrap to the next row when the image would go past the sidebar
                if x > rect.right - image.get_width():
                    x = start_x
                    y += image.get_height() + 4
            # fall back to a text label if an image is missing
            else:
                label = small.render(piece, True, (0, 0, 0))
                screen.blit(label, (x, y))
                x += 18
                # wrap text labels to the next row too
                if x > rect.right - 18:
                    x = start_x
                    y += 20

    draw_capture_list(white_captured, rect.x + 5, rect.y + 25)
    draw_capture_list(black_captured, rect.x + 5, mid_y + 25)
        

def draw_bottom_ui(player_names, current_player, white_time, black_time):
    # draw player names, clocks, and turn highlight under the board
    white_name, black_name = player_names if player_names else ("White", "Black")
    panel_y = BOARD_HEIGHT
    panel_height = INFO_BAR_HEIGHT
    panel_width = WIDTH // 2

    white_rect = pygame.Rect(0, panel_y, panel_width, panel_height)
    black_rect = pygame.Rect(panel_width, panel_y, panel_width, panel_height)

    pygame.draw.rect(screen, (245, 245, 245), white_rect)
    pygame.draw.rect(screen, (245, 245, 245), black_rect)
    pygame.draw.rect(screen, (0, 0, 0), white_rect, 2)
    pygame.draw.rect(screen, (0, 0, 0), black_rect, 2)

    # outline the side whose turn it is
    if current_player == "w":
        pygame.draw.rect(screen, (255, 215, 0), white_rect, 4)
    else:
        pygame.draw.rect(screen, (255, 215, 0), black_rect, 4)

    title_font = pygame.font.Font(None, 28)
    info_font = pygame.font.Font(None, 24)

    white_title = title_font.render("White", True, (0, 0, 0))
    black_title = title_font.render("Black", True, (0, 0, 0))
    white_label = info_font.render(white_name or "White", True, (0, 0, 0))
    black_label = info_font.render(black_name or "Black", True, (0, 0, 0))
    white_time_text = info_font.render(f"Time: {format_time(white_time)}", True, (0, 0, 0))
    black_time_text = info_font.render(f"Time: {format_time(black_time)}", True, (0, 0, 0))
    white_turn = info_font.render("Your turn" if current_player == "w" else "", True, (0, 100, 0))
    black_turn = info_font.render("Your turn" if current_player == "b" else "", True, (0, 100, 0))

    screen.blit(white_title, (white_rect.x + 12, panel_y + 8))
    screen.blit(black_title, (black_rect.x + 12, panel_y + 8))
    screen.blit(white_label, (white_rect.x + 12, panel_y + 34))
    screen.blit(black_label, (black_rect.x + 12, panel_y + 34))
    screen.blit(white_time_text, (white_rect.x + 12, panel_y + 56))
    screen.blit(black_time_text, (black_rect.x + 12, panel_y + 56))

    # show the turn label on the active player's panel
    if current_player == "w":
        screen.blit(white_turn, (white_rect.right - white_turn.get_width() - 12, panel_y + 34))
    else:
        screen.blit(black_turn, (black_rect.right - black_turn.get_width() - 12, panel_y + 34))


def timer_screen():
    # show the timeout screen when a player's clock reaches zero
    font = pygame.font.Font(None, 48)
    text = font.render("Time's up! Draw!", True, (255, 0, 0))

    # keep the timeout screen open until the window is closed
    while True:
        # listen for the window close event
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return

        screen.fill((238, 238, 210))
        screen.blit(text, (WIDTH // 2 - text.get_width() // 2, HEIGHT // 2 - text.get_height() // 2))
        info = font.render("Close window to exit", True, (0, 0, 0))
        screen.blit(info, (WIDTH // 2 - info.get_width() // 2, HEIGHT // 2 + 60))
        pygame.display.flip()

if __name__ == "__main__":
    # start at the menu, then collect names and launch the game
    if display_menu():
        player_names = input_screen()
        main(player_names)  


