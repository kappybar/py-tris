from lib import *
import evaluator

# 占有しようとしている場所がちゃんと空白になっているかチェックする
def isValidPlace(mainBoard, occupiedPositions:List[Tuple[int]]) -> bool:
    for place in occupiedPositions:
        # 盤面の左右の外にはみ出ていないこと
        if not 0 <= place[0] < BOARD_WIDTH:
            return False
        # 盤面の上下の外にはみ出ていないこと
        if not 0 <= place[1] < BOARD_HEIGHT:
            return False
        # placeの場所が空白であること
        if mainBoard[place[1]][place[0]] is not MINO.NONE:
            return False
    
    return True

# moveの方向にdirectedMinoを回転しようとしたとき，directedMinoが回転成功するならば実行後のdirectedMinoを，回転失敗するならばNoneを返す
def Rotate (directedMino:DirectedMino, move:MOVE, mainBoard) -> Union[None, DirectedMino]:
    """
    以下，Tetris Design GuidelineにおけるSRSの内容を要約したものである。

    テトリスにおける回転入れは，Iミノ以外の場合，以下の流れがとられる（SRSと呼ばれる）:

    1. 中心位置を変えずにそのままの場所で回転する
    2. 中心位置を左右に動かす
    3. その状態から中心位置を上下に動かす
    4. 元に戻し，中心位置を上下に2マス動かす
    5. その状態から中心位置を左右に動かす

    上の5種類全て失敗した場合のみ，回転入れが失敗となり，ミノはその場にとどまる。なお，左右・上下のどちらに移動するかは初期状態・回転方向に依存する。

    Iミノの場合も同様だが，やや違いがある。詳しくはガイドラインを参照。
    """

    # Iミノの回転入れ
    if directedMino.mino is MINO.I:
        offsets = OFFSETS_I[directedMino.direction][move]
    # Iミノ以外のミノの回転入れ
    else:
        offsets = OFFSETS_EXCEPT_I[directedMino.direction][move]

    # SRSに従って上記の1~5を順番に実行する
    for i in range(len(offsets)):
        newDirectedMino = DirectedMino(
            directedMino.mino,
            GetNewDirection(directedMino.direction, move),
            (directedMino.pos[0] + offsets[i][0], directedMino.pos[1] + offsets[i][1])
        )
        occupiedPositons = GetOccupiedPositions(newDirectedMino)
        if isValidPlace(mainBoard, occupiedPositons):
            return newDirectedMino
    
    # どれも失敗してしまった場合
    return None


# minoを今の位置からdirectionを変えずに左右に動かして得られるminoのリストを返す
def GetSideMovedMinos (board:Board, mino:DirectedMino) -> List[Tuple[DirectedMino, List[MOVE]]]:
    sideMovedMinos = []

    # 左に動かしていく
    # 左右移動を一回もしない場合はこちら側に含める（そのためにxに+1している）
    x,y = mino.pos[0] + 1, mino.pos[1]
    count = -1
    while True:
        x -= 1
        count += 1
        newMino = DirectedMino(
            mino.mino,
            mino.direction,
            (x,y)
        )
        occupiedPositions = GetOccupiedPositions(newMino)
        if isValidPlace(board.mainBoard, occupiedPositions):
            sideMovedMinos.append((newMino, [MOVE.LEFT for _ in range(count)]))
        else:
            break
    
    # 右に動かしていく
    x,y = mino.pos[0], mino.pos[1]
    count = 0
    while True:
        x += 1
        count += 1
        newMino = DirectedMino(
            mino.mino,
            mino.direction,
            (x,y)
        )
        occupiedPositions = GetOccupiedPositions(newMino)
        if isValidPlace(board.mainBoard, occupiedPositions):
            sideMovedMinos.append((newMino, [MOVE.RIGHT for _ in range(count)]))
        else:
            break
    
    return sideMovedMinos

# minoを今の位置で1回だけ回転を試みた場合に得られるminoのリストに，回転を全く試みない場合を足して返す
def GetRotatedMinos (board:Board, mino:DirectedMino) -> List[Tuple[DirectedMino, List[MOVE]]]:
    rotatedMinos = []

    # 回転なし
    rotatedMinos.append((mino, []))

    # 左回転
    directedMino = Rotate(mino, MOVE.L_ROT, board.mainBoard)
    if directedMino is not None:
        rotatedMinos.append((directedMino, [MOVE.L_ROT]))
    
    # 右回転
    directedMino = Rotate(mino, MOVE.R_ROT, board.mainBoard)
    if directedMino is not None:
        rotatedMinos.append((directedMino, [MOVE.R_ROT]))
    
    return rotatedMinos

# 受け取ったdirectedMinoをいけるところまで下に落とす。何個分おとせるかを返す
def Drop(mainBoard, directedMino:DirectedMino) -> int:
    dropCount = 0
    occupiedPositions = GetOccupiedPositions(directedMino)

    while True:
        # occupiedPostionsの全ての要素を一つずつ下に落とす
        for i in range(len(occupiedPositions)):
            occupiedPositions[i] = (occupiedPositions[i][0], occupiedPositions[i][1] + 1)
        
        # 一つずつ下に落としたときに，その場所にミノが存在することができればドロップできていることになるのでcountをインクリメントする
        if isValidPlace(mainBoard, occupiedPositions):
            dropCount += 1
        else:
            break
    
    return dropCount
        
# boardとそこに置きたいminoを入力して，
# (ミノがおける場所，そこにたどり着く方法)
# という形式のタプルの配列を返す
def GetPossibleMoves(
    board:Board,
    directedMino:DirectedMino,
) -> List[Tuple[DirectedMino, List[MOVE]]]:

    # unmovedNodes, unrotatedNodesを交互に幅優先っぽく探索するほうが最短に近い経路を見つけられるので分けている
    unmovedNodes : List[DirectedMino] = [directedMino]
    unrotatedNodes : List[DirectedMino] = [directedMino]
    
    # 到達できるミノをエンコードしたものと，到達するための経路を結ぶ辞書
    reachableNodes = {
        EncodeDirectedMino(directedMino) : []
    }

    while unmovedNodes or unrotatedNodes:
        while unmovedNodes:
            unmovedNode = unmovedNodes.pop()
            encodedUnmovedNode = EncodeDirectedMino(unmovedNode)
            sideMovedNodes = GetSideMovedMinos(board, unmovedNode)
            for sideMovedNode, path in sideMovedNodes:
                dropCount = Drop(board.mainBoard, sideMovedNode)
                droppedNode = DirectedMino(
                    sideMovedNode.mino,
                    sideMovedNode.direction,
                    (sideMovedNode.pos[0], sideMovedNode.pos[1] + dropCount)
                )
                encodedDroppedNode = EncodeDirectedMino(droppedNode)
                if encodedDroppedNode not in reachableNodes:
                    unrotatedNodes.append(droppedNode)
                    reachableNodes[encodedDroppedNode] = reachableNodes[encodedUnmovedNode] + path + [MOVE.DOWN for _ in range(dropCount)]
        
        while unrotatedNodes:
            unrotatedNode = unrotatedNodes.pop()
            encodedUnrotatedNode = EncodeDirectedMino(unrotatedNode)
            rotatedNodes = GetRotatedMinos(board, unrotatedNode)
            for rotatedNode, path in rotatedNodes:
                dropCount = Drop(board.mainBoard, rotatedNode)
                droppedNode = DirectedMino(
                    rotatedNode.mino,
                    rotatedNode.direction,
                    (rotatedNode.pos[0], rotatedNode.pos[1] + dropCount)
                )
                encodedDroppedNode = EncodeDirectedMino(droppedNode)
                if encodedDroppedNode not in reachableNodes:
                    unmovedNodes.append(droppedNode)
                    unrotatedNodes.append(droppedNode) # 回転は複数回やることによって生まれる盤面もある
                    reachableNodes[encodedDroppedNode] = reachableNodes[encodedUnrotatedNode] + path + [MOVE.DOWN for _ in range(dropCount)]

    # 結果出力
    possibleMoves = []
    # 方向は異なるが占領する場所は同じになるミノが存在するので，これらを重複して数えないために利用する
    # 例えばzミノはNとSで位置をずらせば同じ場所を占領するようになる
    encodedPlacesList = set()
    for key in reachableNodes:
        # 最後には必ずMOVE.DROPをつける
        # 最後にMOVE.DROPをつけるので，最後の連続するMOVE.DOWNは消去できる
        path = reachableNodes[key]
        count = 0
        while count < len(path):
            if path[-(count + 1)] is MOVE.DOWN:
                count += 1
            else:
                break
        path = path[:len(path) - count] + [MOVE.DROP]
        decodedMino = DecodeDirectedMino(key)
        encodedPlaces = EncodePlacesOccupiedByDirectedMino(decodedMino)
        if encodedPlaces in encodedPlacesList:
            # possibleMovesの中から同じ位置を占領することになるdirectedMinoを探索
            sameMino, samePath = None, None
            for mino, path in possibleMoves:
                if (
                    EncodePlacesOccupiedByDirectedMino(mino) == encodedPlaces
                ):
                    sameMino, samePath = mino, path
                    break
            # 今回考えているpathの方が短かったら入れ替え
            possibleMoves.remove((sameMino, samePath))
            possibleMoves.append((decodedMino, path))
        if encodedPlaces not in encodedPlacesList:
            possibleMoves.append((
                decodedMino,
                path
            ))
            encodedPlacesList.add(encodedPlaces)
    
    return possibleMoves

def Search (board:Board, mino:DirectedMino, path:List[MOVE], limit:int) -> int:
    # 最後のみ盤面自体の評価を行う
    if limit == 0:
        # ライン消去
        joinedBoard = JoinDirectedMinoToBoard(mino, board)
        newMainBoard, clearedRowCount = ClearLines(joinedBoard.mainBoard)
        return evaluator.EvalPath(path, clearedRowCount) + evaluator.EvalMainBoard(newMainBoard)
    
    # ライン消去
    joinedBoard = JoinDirectedMinoToBoard(mino, board)
    newMainBoard, clearedRowCount = ClearLines(joinedBoard.mainBoard)
    clearedBoard = Board(
        newMainBoard,
        DirectedMino(
            board.followingMinos[0],
            FIRST_MINO_DIRECTION,
            FIRST_MINO_POS
        ),
        board.followingMinos[1:] + [MINO.NONE],
        board.holdMino,
        True
    )

    possibleMoves = GetPossibleMoves(
        clearedBoard,
        clearedBoard.currentMino
    )

    maxValue = -10000000000
    for possibleMoveMino, possibleMovePath in possibleMoves:
        value = Search(clearedBoard, possibleMoveMino, possibleMovePath, limit-1)
        if value >= maxValue:
            maxValue = value

    return maxValue + evaluator.EvalPath(path, clearedRowCount)

# 実際に手を決める関数
def Decide (board:Board) -> Tuple[DirectedMino, List[MOVE]]:

    possibleMoves = GetPossibleMoves(
        board,
        board.currentMino
    )

    maxValue, maxMino, maxPath = -10000000000, None, None
    for mino, path in possibleMoves:
        # 評価値計算
        value = Search(board, mino, path, 2-1)
        if value >= maxValue:
            maxMino, maxPath = mino, path
            maxValue = value
    
    return maxValue, maxMino, maxPath