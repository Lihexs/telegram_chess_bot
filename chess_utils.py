import chess

# Mapping of pieces to their Unicode symbols for both white and black
unicode_pieces = {
    chess.PAWN: '♙',
    chess.KNIGHT: '♘',
    chess.BISHOP: '♗',
    chess.ROOK: '♖',
    chess.QUEEN: '♕',
    chess.KING: '♔',
}

black_unicode_pieces = {
    chess.PAWN: '♟︎',
    chess.KNIGHT: '♞',
    chess.BISHOP: '♝',
    chess.ROOK: '♜',
    chess.QUEEN: '♛',
    chess.KING: '♚',
}

def board_to_unicode(board):
    """Converts a chess board to a string with Unicode symbols."""
    unicode_board = ""
    for square in chess.SQUARES_180:
        piece = board.piece_at(square)
        if piece:  # If there's a piece on the square
            color = piece.color
            piece_type = piece.piece_type
            # Choose the appropriate symbol based on the piece's color
            symbol = unicode_pieces[piece_type] if color == chess.WHITE else black_unicode_pieces[piece_type]
        else:
            symbol = "□"
        # Check if the square is in the last file (H), which corresponds to 7
        unicode_board += symbol + (" " if chess.square_file(square) != 7 else "\n")
    return unicode_board


