from PIL import Image, ImageDraw
import chess

# Load images for chess pieces
piece_images = {
    'bB': Image.open('./utils/bB.png'),
    'bK': Image.open('./utils/bK.png'),
    'bN': Image.open('./utils/bN.png'),
    'bP': Image.open('./utils/bP.png'),
    'bQ': Image.open('./utils/bQ.png'),
    'bR': Image.open('./utils/bR.png'),
    'wB': Image.open('./utils/wB.png'),
    'wK': Image.open('./utils/wK.png'),
    'wN': Image.open('./utils/wN.png'),
    'wP': Image.open('./utils/wP.png'),
    'wQ': Image.open('./utils/wQ.png'),
    'wR': Image.open('./utils/wR.png'),
}


# Function to draw the board and place pieces on it
def draw_board_with_pieces(board):
    square_size = 60  # Define the size of a square on the board
    board_image = Image.new('RGB', (square_size * 8, square_size * 8), 'white')
    draw = ImageDraw.Draw(board_image)

    # Draw the squares on the board
    for file in range(8):
        for rank in range(8):
            x0 = file * square_size
            y0 = (7 - rank) * square_size
            x1 = x0 + square_size
            y1 = y0 + square_size
            if (file + rank) % 2 == 0:
                fill_color = '#D2B48C'  # light square
            else:
                fill_color = '#8B4513'  # dark square
            draw.rectangle([x0, y0, x1, y1], fill=fill_color)
    # Place pieces on the board
    for square in chess.SQUARES:
        piece = board.piece_at(square)
        if piece:
            # Get the piece symbol in uppercase and prepend the color prefix to it
            color = 'w' if piece.color == chess.WHITE else 'b'
            symbol = color + piece.symbol().upper()  # This will be 'wR' for white rook, 'bR' for black rook, etc.
            piece_image = piece_images[symbol]  # Use the corrected key to access the image
            # Calculate the top-left corner of the square to place the piece image
            file = chess.square_file(square)
            rank = chess.square_rank(square)
            x0 = file * square_size
            y0 = (7 - rank) * square_size
            # Paste the piece image onto the board image
            board_image.paste(piece_image, (x0, y0), piece_image)

    return board_image

# Example usage:
# Create a new chess board
board = chess.Board()
# Draw the board with pieces
board_img = draw_board_with_pieces(board)
# Save the board image to a file
board_img_path = 'utils/chess_board_with_pieces.png'
board_img.save(board_img_path)
board_img_path