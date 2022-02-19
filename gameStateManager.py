import initSettings
import boardWatcher
import decisionMaker
import simulator
from lib import *

# ゲーム画面を認識して標準出力に出力する関数（無限ループ）
def PytrisBoardWatcher ():
    print("\n\nPy-tris Board Watcher\n\n")

    # ゲームの再開
    PressEnter()
    time.sleep(0.5)

    # 盤面を出力する分の行数を確保する
    for _ in range(BOARD_HEIGHT):
        print("", flush=True)
    
    # boardオブジェクトの生成
    board = Board()

    # メインループ
    while True:
        with mss.mss() as sct:
            a = Timer()
            # キャプチャする範囲は1P側の半分で十分
            region = {'top': WINDOW_Y, 'left': WINDOW_X, 'width': WINDOW_WIDTH / 2, 'height': WINDOW_HEIGHT}
            img = sct.grab(region)
            img = Image.frombytes("RGB", img.size, img.bgra, "raw", "BGRX")
            board.mainBoard = boardWatcher.GetMainBoardWithColor(img)
            board.followingMinos = boardWatcher.GetFollowingMinos(img)
            board.holdMino = boardWatcher.GetHoldMino(img)
            PrintBoardWithColor(board, True, a.Stop())


def main():
    # ゲームの初期設定
    initSettings.Init()
    
    # # 盤面監視モード
    # PytrisBoardWatcher()


    # 適当に盤面を生成
    board = Board()

    for i in range(10):
        board.AddMinoToMainBoard((i,30), MINO.JAMA)
        board.AddMinoToMainBoard((i,31), MINO.JAMA)
    board.DeleteMinoInMainBoard((6,30))
    board.AddMinoToMainBoard((7,28), MINO.JAMA)

    board.followingMinos = [simulator.GenerateMino() for _ in range(FOLLOWING_MINOS_COUNT)]
    print("\n\n\n")
    PrintBoardWithColor(board)

    while True:
        addedMino = simulator.GenerateMino()
        board = simulator.AddFollowingMino(board, addedMino)

        # 思考ルーチン
        possibleMoves = decisionMaker.GetPossibleMoves(
            board,
            board.currentMino
        )
        mino, path = possibleMoves[-1]

        board = simulator.PutMino(path, board.currentMino, board)

        newMainBoard, clearedRowCount = simulator.ClearLinesOfBoard(board)
        board = Board(
            newMainBoard,
            None,
            board.followingMinos,
            board.holdMino,
            True
        )

