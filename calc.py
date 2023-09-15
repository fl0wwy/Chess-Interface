# A python file which contains functions for calculation of possible moves

def horizontal_calc(instance):
    """Funcion which calculates horizontal line possible moves (for Rook and Queen)"""
    poss = []
    neg_thersh = float('-inf')
    pos_thersh = float('inf')
    for row in instance.board.GRID:
        for rect in row:
            if rect == instance.board.square_dict[instance.square]:
                continue
            if rect.centery == instance.board.square_dict[instance.square].centery:
                pos = list(instance.board.square_dict.values()).index(rect)
                key = list(instance.board.square_dict.keys())[pos] 
                if key in instance.board.occ_squares:
                    if instance.board.occ_squares[key].color == instance.color:
                        if rect.centerx < instance.board.square_dict[instance.square].centerx:
                            if rect.centerx > neg_thersh:
                                neg_thersh = rect.centerx
                        else:
                            if rect.centerx < pos_thersh:
                                pos_thersh = rect.centerx
                    else:
                        if rect.centerx < instance.board.square_dict[instance.square].centerx:
                            if rect.centerx > neg_thersh:
                                neg_thersh = rect.centerx - 100
                        else:
                            if rect.centerx < pos_thersh:
                                pos_thersh = rect.centerx + 100
                poss.append(rect)
    
    copy = poss.copy()                 
    for rect in poss:
        if rect.centerx <= neg_thersh:
            copy.remove(rect)
        if rect.centerx >= pos_thersh:
            copy.remove(rect)  
    return copy 

def vertical_calc(instance):
    """Function which calculates vertical line possible moves (for rook and queen)"""
    poss = []
    neg_thersh = float('-inf')
    pos_thersh = float('inf')
    for row in instance.board.GRID:
        for rect in row:
            if rect == instance.board.square_dict[instance.square]:
                continue
            if rect.centerx == instance.board.square_dict[instance.square].centerx:
                pos = list(instance.board.square_dict.values()).index(rect)
                key = list(instance.board.square_dict.keys())[pos] 
                if key in instance.board.occ_squares:
                    if instance.board.occ_squares[key].color == instance.color:
                        if rect.centery < instance.board.square_dict[instance.square].centery:
                            if rect.centery > neg_thersh:
                                neg_thersh = rect.centery
                        else:
                            if rect.centery < pos_thersh:
                                pos_thersh = rect.centery
                    else:
                        if rect.centery < instance.board.square_dict[instance.square].centery:
                            if rect.centery > neg_thersh:
                                neg_thersh = rect.centery - 100
                        else:
                            if rect.centery < pos_thersh:
                                pos_thersh = rect.centery + 100
                poss.append(rect)
    
    copy = poss.copy()                 
    for rect in poss:
        if neg_thersh != None:
            if rect.centery <= neg_thersh:
                copy.remove(rect)  
        if pos_thersh != None:
            if rect.centery >= pos_thersh:
                copy.remove(rect)    
    return copy   

def diagonal_calc(instance):
    """Function which calculates diagonal lines possible moves (for bishop and queen)"""
    def topDown():
        """Calculates diagonal from top to bottom"""
        candidates = []
        ceil_y = floor_y = instance.board.square_dict[instance.square].centery
        pos_x = neg_x = instance.board.square_dict[instance.square].centerx
        pos_thresh = [float('-inf'), float('-inf')]
        neg_thresh = [float('inf'), float('inf')]
        while ceil_y >= 50 or floor_y <= 750:
            ceil_y -= 100
            floor_y += 100
            neg_x -= 100
            pos_x += 100
            for row in instance.board.GRID:
                for rect in row:
                    if rect.center == (neg_x, ceil_y):
                        pos = list(instance.board.square_dict.values()).index(rect)
                        key = list(instance.board.square_dict.keys())[pos] 
                        if key in instance.board.occ_squares:
                            if instance.board.occ_squares[key].color == instance.color:
                                if pos_thresh[0] < rect.centerx:
                                    pos_thresh = list(rect.center)
                            else:   
                                if pos_thresh[0] < rect.centerx:
                                    pos_thresh = [rect.centerx - 100, rect.centery - 100]
                        candidates.append(rect)               
                    elif rect.center == (pos_x, floor_y):   
                        pos = list(instance.board.square_dict.values()).index(rect)
                        key = list(instance.board.square_dict.keys())[pos] 
                        if key in instance.board.occ_squares:
                            if instance.board.occ_squares[key].color == instance.color:
                                if neg_thresh[0] > rect.centerx:
                                    neg_thresh = list(rect.center)
                            else:   
                                if neg_thresh[0] > rect.centerx:
                                    neg_thresh = [rect.centerx + 100, rect.centery + 100]
                        candidates.append(rect)
        copy = candidates.copy()
        for rect in candidates:
            if rect.centerx >= neg_thresh[0] and rect.centery >= neg_thresh[1]:
                copy.remove(rect)
            elif rect.centerx <= pos_thresh[0] and rect.centery <= pos_thresh[1]: 
                copy.remove(rect)
        return copy 
    
    def downTop():
        """Calculates diagonal from bottom to top"""
        candidates = []
        ceil_y = floor_y = instance.board.square_dict[instance.square].centery
        pos_x = neg_x = instance.board.square_dict[instance.square].centerx
        pos_thresh = [float('inf'), float('-inf')]
        neg_thresh = [float('-inf'), float('inf')]
        while ceil_y >= 50 or floor_y <= 750:
            ceil_y -= 100
            floor_y += 100
            neg_x -= 100
            pos_x += 100
            for row in instance.board.GRID:
                for rect in row:
                    if rect.center == (pos_x, ceil_y):
                        pos = list(instance.board.square_dict.values()).index(rect)
                        key = list(instance.board.square_dict.keys())[pos] 
                        if key in instance.board.occ_squares:
                            if instance.board.occ_squares[key].color == instance.color:
                                if pos_thresh[0] > rect.centerx:
                                    pos_thresh = list(rect.center)
                            else:   
                                if pos_thresh[0] > rect.centerx:
                                    pos_thresh = [rect.centerx + 100, rect.centery - 100]
                        candidates.append(rect)
                    elif rect.center == (neg_x, floor_y):
                        pos = list(instance.board.square_dict.values()).index(rect)
                        key = list(instance.board.square_dict.keys())[pos] 
                        if key in instance.board.occ_squares:
                            if instance.board.occ_squares[key].color == instance.color:
                                if neg_thresh[0] < rect.centerx:
                                    neg_thresh = list(rect.center)
                            else:   
                                if neg_thresh[0] < rect.centerx:
                                    neg_thresh = [rect.centerx - 100, rect.centery + 100]
                        candidates.append(rect)
        copy = candidates.copy()
        for rect in candidates:
            if rect.centerx <= neg_thresh[0] and rect.centery >= neg_thresh[1]:
                copy.remove(rect)
            elif rect.centerx >= pos_thresh[0] and rect.centery <= neg_thresh[1]: 
                copy.remove(rect)
        return copy                  

    moves = downTop()
    moves.extend(topDown())
    return moves  

def detect_pseudo_moves(instance, move_list : list):
    """Plays all possible moves of the chosen piece and checks if the move is legal
    (adversary is not able to capture the king)

    Args:
        instance (pg.sprite): The playing piece
        move_list (list): The list of all calculated moves

    Returns:
        list: All legal moves that can be made.
    """
    if move_list is None:
        return []
    legal_moves = move_list.copy()
    
    current_pos = instance.board.square_dict[instance.square]
    en_passant = instance.board.en_passant
    
    for move in move_list:
        res_piece = instance.play(move, True)
        for piece in instance.board.pieces["black"].sprites() if instance.color == "White" else instance.board.pieces["white"].sprites():
            adv_moves = piece.possible_moves()
            if adv_moves is None:
                continue
            for adv_move in adv_moves:
                idx = list(instance.board.square_dict.values()).index(adv_move)
                key = list(instance.board.square_dict.keys())[idx]
                if key in instance.board.occ_squares:
                    if instance.board.occ_squares[key].icon == "king":
                        legal_moves.remove(move)
                        break
            else:
                continue
            break      
        
        instance.play(current_pos, True)
        instance.board.en_passant = en_passant
        
        if res_piece is not None:
            if instance.color == "White":
                instance.board.pieces["black"].add(res_piece)
            else:
                instance.board.pieces["white"].add(res_piece)      
            instance.board.occ_squares[res_piece.square] = res_piece   
    return legal_moves             