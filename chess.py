# Imported two libraries:
# pygame → used to create the game window, graphics, input handling, and game loop
# os → used to access file paths (for loading images from folders)
import pygame
import os


# Initializes all pygame modules (graphics, sound, fonts, input, etc.)
pygame.init()


# Window size (board 640x640 plus sidebar and bottom UI panel)
BOARD_HEIGHT = 640
INFO_BAR_HEIGHT = 80
WIDTH, HEIGHT = 800, BOARD_HEIGHT + INFO_BAR_HEIGHT

# Size of each chess square
SQUARE_SIZE = 80

# RGB color values for chessboard and highlights
WHITE = (238, 238, 210)   # light squares
GREEN = (118, 150, 86)    # dark squares
YELLOW = (255, 255, 0)    # move highlight


# Creates the game window
screen = pygame.display.set_mode((WIDTH, HEIGHT))

# Sets title at top of window
pygame.display.set_caption("Chess Game")


# Load piece images into a dictionary for easy access

def load_images():

    pieces = {}

    # Maps piece codes → image file names
    piece_files = {
        "wP": "White_Pawn.png", "wR": "White_Rook.png", "wH": "White_Horse.png",
        "wB": "White_Bishop.png", "wQ": "White_Queen.png", "wK": "White_King.png",
        "bP": "Black_Pawn.png", "bR": "Black_Rook.png", "bH": "Black_Horse.png",
        "bB": "Black_Bishop.png", "bQ": "Black_Queen.png", "bK": "Black_King.png"
    }

    # Loop through dictionary and load each image
    for key, filename in piece_files.items():

        # Build correct file path (assets/filename)
        path = os.path.join("assets", filename)

        # Load image from disk
        img = pygame.image.load(path)

        # Resize image to fit one chess square
        pieces[key] = pygame.transform.scale(img, (SQUARE_SIZE, SQUARE_SIZE))

    return pieces


# Stores all loaded images globally for quick access
IMAGES = load_images()
SMALL_IMAGES = {key: pygame.transform.scale(img, (32, 32)) for key, img in IMAGES.items()}

# Background helper uses piece images from assets to decorate title and lose screens.
def draw_screen_background():
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
    for key, pos, size in zip(bg_pieces, positions, sizes):
        img = pygame.transform.smoothscale(IMAGES[key], (size, size))
        img.set_alpha(60)
        screen.blit(img, pos)
    overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
    overlay.fill((238, 238, 210, 180))
    screen.blit(overlay, (0, 0))

# 8x8 chess board represented as a 2D list
# Each element is a string:
# "wP" = white pawn, "bR" = black rook, "--" = empty square
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

# Track captured pieces for each player
white_captured = []
black_captured = []



def board_to_screen(row, col, flipped):
    if flipped:
        row = 7 - row
        col = 7 - col
    return col * SQUARE_SIZE, row * SQUARE_SIZE


def screen_to_board(pos, flipped):
    col = pos[0] // SQUARE_SIZE
    row = pos[1] // SQUARE_SIZE
    if flipped:
        row = 7 - row
        col = 7 - col
    return row, col


def draw_board(flipped=False):
    # Draws the chessboard using alternating colors for squares.
    for r in range(8):       # loop rows
        for c in range(8):   # loop columns

            # Alternating square colors (checker pattern)
            if (r + c) % 2 == 0:
                color = WHITE
            else:
                color = GREEN

            x, y = board_to_screen(r, c, flipped)

            pygame.draw.rect(
                screen,
                color,
                (x, y, SQUARE_SIZE, SQUARE_SIZE)
            )


def draw_pieces(flipped=False):

    for r in range(8):
        for c in range(8):

            piece = board[r][c]

            # Only draw if square is not empty
            if piece != "--":

                # Draw image at correct pixel position
                x, y = board_to_screen(r, c, flipped)
                screen.blit(IMAGES[piece], (x, y))


def get_valid_moves(row, col):

    moves = []
    piece = board[row][col]

    knight_moves = [
        (-2, -1), (-2, 1),
        (-1, -2), (-1, 2),
        (1, -2), (1, 2),
        (2, -1), (2, 1)
    ]

    # If selected piece is a knight
    if piece in ["wH", "bH"]:

        for dr, dc in knight_moves:

            r, c = row + dr, col + dc

            # Check if inside board
            if 0 <= r < 8 and 0 <= c < 8:

                # White knight rules
                if piece == "wH":
                    # can move to empty OR capture black
                    if board[r][c] == "--" or board[r][c][0] == "b":
                        moves.append((r, c))

                # Black knight rules
                else:
                    if board[r][c] == "--" or board[r][c][0] == "w":
                        moves.append((r, c))
            
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


    # Black Pawn movement logic (similar to white but in opposite direction)
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
                    moves.append((r, c))  # capture
                    break

                elif piece == "bR" and board[r][c][0] == "w":
                    moves.append((r, c))  # capture
                    break

                else:
                    break  # same color piece blocks
                r += dr
                c += dc

# Bishop
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


# Queen movememnt logic is a combination of rook + bishop
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


# King moves
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

        # Castling options
        if col == 4:
            if piece == "wK" and row == 7:
                if board[7][7] == "wR" and board[7][5] == "--" and board[7][6] == "--":
                    moves.append((7, 6))
                if board[7][0] == "wR" and board[7][1] == "--" and board[7][2] == "--" and board[7][3] == "--":
                    moves.append((7, 2))
            elif piece == "bK" and row == 0:
                if board[0][7] == "bR" and board[0][5] == "--" and board[0][6] == "--":
                    moves.append((0, 6))
                if board[0][0] == "bR" and board[0][1] == "--" and board[0][2] == "--" and board[0][3] == "--":
                    moves.append((0, 2))

    return moves


def king_present():
    white_king = False
    black_king = False

    for row in board:
        for square in row:
            if square == "wK":
                white_king = True
            elif square == "bK":
                black_king = True

    return white_king and black_king

def pawn_promotion(row, col):
    piece = board[row][col]
    if piece == "wP" and row == 0:
        board[row][col] = "wQ"  # promote to queen
    elif piece == "bP" and row == 7:
        board[row][col] = "bQ"  # promote to queen


def castling(row, col):
    if board[row][col] == "wK" and col == 4:
        # Kingside castling
        if board[row][7] == "wR" and board[row][5] == "--" and board[row][6] == "--":
            board[row][6] = "wK"
            board[row][5] = "wR"
            board[row][4] = "--"
            board[row][7] = "--"
        # Queenside castling
        elif board[row][0] == "wR" and board[row][1] == "--" and board[row][2] == "--" and board[row][3] == "--":
            board[row][2] = "wK"
            board[row][3] = "wR"
            board[row][4] = "--"
            board[row][0] = "--"
    elif board[row][col] == "bK" and col == 4:
        # Kingside castling
        if board[row][7] == "bR" and board[row][5] == "--" and board[row][6] == "--":
            board[row][6] = "bK"
            board[row][5] = "bR"
            board[row][4] = "--"
            board[row][7] = "--"
        # Queenside castling
        elif board[row][0] == "bR" and board[row][1] == "--" and board[row][2] == "--" and board[row][3] == "--":
            board[row][2] = "bK"
            board[row][3] = "bR"
            board[row][4] = "--"
            board[row][0] = "--"
    return board[row][col] in ["wK", "bK"]  


def format_time(seconds):
    minutes = int(seconds) // 60
    sec = int(seconds) % 60
    return f"{minutes:02d}:{sec:02d}"


def is_square_attacked(target_row, target_col, by_player):
    for r in range(8):
        for c in range(8):
            piece = board[r][c]
            if piece != "--" and piece[0] == by_player:
                moves = get_valid_moves(r, c)
                if (target_row, target_col) in moves:
                    return True
    return False


def is_in_check(player):
    king_code = player + "K"
    for r in range(8):
        for c in range(8):
            if board[r][c] == king_code:
                opponent = "b" if player == "w" else "w"
                return is_square_attacked(r, c, opponent)
    return False


def _simulate_move(sr, sc, tr, tc):
    saved = {}
    saved['from'] = (sr, sc, board[sr][sc])
    saved['to'] = (tr, tc, board[tr][tc])
    piece = board[sr][sc]

    board[tr][tc] = piece
    board[sr][sc] = "--"

    # handle castling rook in simulation
    if piece in ["wK", "bK"] and abs(tc - sc) == 2:
        if tc > sc:
            saved['rook'] = (tr, 7, board[tr][7])
            saved['rook_target'] = (tr, 5)
            board[tr][5] = board[tr][7]
            board[tr][7] = "--"
        else:
            saved['rook'] = (tr, 0, board[tr][0])
            saved['rook_target'] = (tr, 3)
            board[tr][3] = board[tr][0]
            board[tr][0] = "--"

    # promotion
    if board[tr][tc] == "wP" and tr == 0:
        saved['promo'] = True
        board[tr][tc] = "wQ"
    elif board[tr][tc] == "bP" and tr == 7:
        saved['promo'] = True
        board[tr][tc] = "bQ"

    return saved


def _undo_simulation(saved):
    sr, sc, from_piece = saved['from']
    tr, tc, to_piece = saved['to']
    board[sr][sc] = from_piece
    board[tr][tc] = to_piece
    if 'rook' in saved:
        rr, rc, rpiece = saved['rook']
        board[rr][rc] = rpiece
        # clear the rook's temporary castling destination if it was moved
        if 'rook_target' in saved:
            trr, trc = saved['rook_target']
            board[trr][trc] = "--"


def get_legal_moves(row, col):
    piece = board[row][col]
    if piece == "--":
        return []
    owner = piece[0]
    possible = get_valid_moves(row, col)
    legal = []
    for tr, tc in possible:
        saved = _simulate_move(row, col, tr, tc)
        still_in_check = is_in_check(owner)
        _undo_simulation(saved)
        if not still_in_check:
            legal.append((tr, tc))
    return legal


def has_any_legal_moves(player):
    for r in range(8):
        for c in range(8):
            if board[r][c] != "--" and board[r][c][0] == player:
                if get_legal_moves(r, c):
                    return True
    return False


def main(player_names):
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

    while running:
        dt = clock.tick(60) / 1000.0
        if current_player == "w":
            white_time -= dt
            if white_time <= 0:
                white_time = 0
                timer_screen()
                running = False
        else:
            black_time -= dt
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

        for event in pygame.event.get():

            # exit game
            if event.type == pygame.QUIT:
                running = False

            # mouse click event
            elif event.type == pygame.MOUSEBUTTONDOWN:

                pos = pygame.mouse.get_pos()
                if pos[0] >= SQUARE_SIZE * 8 or pos[1] >= BOARD_HEIGHT:
                    continue

                # convert pixel → board coordinates
                row, col = screen_to_board(pos, flipped)

                # SELECT PIECE
                if selected_sq is None:

                    if board[row][col] != "--" and board[row][col][0] == current_player:
                        legal = get_legal_moves(row, col)
                        # if king is in check, disallow selecting a piece that cannot resolve check
                        if is_in_check(current_player) and not legal:
                            king_warning = True
                            king_warning_time = pygame.time.get_ticks()
                        else:
                            selected_sq = (row, col)
                            valid_moves = legal

                # MOVE PIECE
                else:
                    if board[row][col] != "--" and board[row][col][0] == current_player:
                        legal = get_legal_moves(row, col)
                        if is_in_check(current_player) and not legal:
                            king_warning = True
                            king_warning_time = pygame.time.get_ticks()
                        else:
                            selected_sq = (row, col)
                            valid_moves = legal
                    else:
                        sr, sc = selected_sq
                        piece = board[sr][sc]

                        # check if move is valid
                        if (row, col) in valid_moves:
                            target = board[row][col]
                            if target != "--":
                                if target[0] == "w":
                                    black_captured.append(target)
                                else:
                                    white_captured.append(target)

                            # move piece and handle castling
                            if piece in ["wK", "bK"] and sc == 4 and abs(col - sc) == 2:
                                board[row][col] = piece
                                board[sr][sc] = "--"
                                if col == 6:
                                    board[row][5] = board[row][7]
                                    board[row][7] = "--"
                                elif col == 2:
                                    board[row][3] = board[row][0]
                                    board[row][0] = "--"
                            else:
                                board[row][col] = piece
                                board[sr][sc] = "--"

                            pawn_promotion(row, col)

                            if not king_present():
                                lose_screen(player_names)
                                running = False
                            else:
                                current_player = "b" if current_player == "w" else "w"

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

    font_title = pygame.font.Font(None, 72)
    font_button = pygame.font.Font(None, 48)

    title_text = font_title.render("En Passant", True, (0, 0, 0))
    start_text = font_button.render("Start", True, (255, 255, 255))

    button_rect = pygame.Rect(WIDTH // 2 - 75, HEIGHT // 2, 150, 60)

    while True:

        for event in pygame.event.get():

            if event.type == pygame.QUIT:
                return False

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
    font = pygame.font.Font(None, 48)
    small = pygame.font.Font(None, 36)

    white_name = ""
    black_name = ""
    active = "white"

    prompt = font.render("Enter Player Names", True, (0, 0, 0))

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return None, None
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_TAB:
                    active = "black" if active == "white" else "white"
                elif event.key == pygame.K_RETURN:
                    if white_name.strip() and black_name.strip():
                        return white_name.strip(), black_name.strip()
                elif event.key == pygame.K_BACKSPACE:
                    if active == "white":
                        white_name = white_name[:-1]
                    else:
                        black_name = black_name[:-1]
                else:
                    char = event.unicode
                    if char.isprintable():
                        if active == "white":
                            white_name += char
                        else:
                            black_name += char

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
    # player_names: (white_name, black_name)
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

        if not w_present and b_present:
            winner = black_name if black_name else "Black"
        elif not b_present and w_present:
            winner = white_name if white_name else "White"
        else:
            winner = "No one"

    text = font.render(f"{winner} wins!", True, (255, 0, 0))

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return

        draw_screen_background()
        screen.blit(text, (WIDTH // 2 - text.get_width() // 2, HEIGHT * 0.40 - text.get_height() // 2))
        info = small.render("Close window to exit", True, (0, 0, 0))
        screen.blit(info, (WIDTH // 2 - info.get_width() // 2, HEIGHT * 0.55 - info.get_height() // 2))
        pygame.display.flip()

def pieces_taken(current_player, white_time, black_time):
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
        if not piece_list:
            none_text = small.render("None", True, (0, 0, 0))
            screen.blit(none_text, (start_x, start_y))
            return

        x = start_x
        y = start_y
        for piece in piece_list:
            image = SMALL_IMAGES.get(piece)
            if image:
                screen.blit(image, (x, y))
                x += image.get_width() + 4
                if x > rect.right - image.get_width():
                    x = start_x
                    y += image.get_height() + 4
            else:
                label = small.render(piece, True, (0, 0, 0))
                screen.blit(label, (x, y))
                x += 18
                if x > rect.right - 18:
                    x = start_x
                    y += 20

    draw_capture_list(white_captured, rect.x + 5, rect.y + 25)
    draw_capture_list(black_captured, rect.x + 5, mid_y + 25)
        

def draw_bottom_ui(player_names, current_player, white_time, black_time):
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

    if current_player == "w":
        screen.blit(white_turn, (white_rect.right - white_turn.get_width() - 12, panel_y + 34))
    else:
        screen.blit(black_turn, (black_rect.right - black_turn.get_width() - 12, panel_y + 34))


def timer_screen():
    font = pygame.font.Font(None, 48)
    text = font.render("Time's up! Draw!", True, (255, 0, 0))

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return

        screen.fill((238, 238, 210))
        screen.blit(text, (WIDTH // 2 - text.get_width() // 2, HEIGHT // 2 - text.get_height() // 2))
        info = font.render("Close window to exit", True, (0, 0, 0))
        screen.blit(info, (WIDTH // 2 - info.get_width() // 2, HEIGHT // 2 + 60))
        pygame.display.flip()

if __name__ == "__main__":
    if display_menu():
        player_names = input_screen()
        main(player_names)  


