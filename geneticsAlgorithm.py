from lib import *
from abc import ABCMeta, abstractmethod
import random
import itertools

# 遺伝的アルゴリズムを実装するための抽象クラス
# このクラスを継承して実際に学習させる

# 1つの個体
class Chromosome(metaclass=ABCMeta):
    @classmethod
    @abstractmethod
    def randomGen(cls):
        # ランダムに1つの個体を生成する。
        # 0世代の生成に使用
        pass

    @abstractmethod
    def fitness(self):
        # 適応度の計算
        # 適応度が高いほど優秀な個体である。
        pass 

    @abstractmethod
    def crossOver(self, other):
        # selfとotheを交叉させて、新しい個体を作る。
        pass 

    @abstractmethod
    def mutation(self):
        # selfを突然変異させる。
        pass


# 遺伝的アルゴリズム自体を行うclass
class GeneticsAlgorithm():
    def __init__(self, n:int, g:int, probCrossOver:float, probMutation:float, generation0):
        assert n == len(generation0)
        assert probCrossOver + probMutation <= 1
        self.n = n
        self.g = g 
        self.probCrossOver = probCrossOver
        self.probMutaion = probMutation
        self.probCopy = 1 - probCrossOver - probMutation
        self.population = generation0
        self.fitness = [0 for _ in range(n)]
        self.cumFitness = [0 for _ in range(n)]
    
    def _CalcFitness(self):
        self.fitness = list(map(lambda x : x.fitness(), self.population))
        self.cumFitness = list(itertools.accumulate(self.fitness))
    
    # ルーレット選択
    # 適応度に比例して個体を選ぶ。
    # 適応度が負になる場合は使えない
    def _RouletteSelection(self):
        fitnessSum = sum(self.fitness)
        prob = random.uniform(0, fitnessSum)
        for i in range(self.n):
            if self.cumFitness[i] > prob:
                return self.population[i]
        assert False

    # トーナメント選択
    # ある一定の集合のサイズを取り出してその中で適応度が高いものを選ぶ
    def _TournamentSelection(self):
        indexSample = random.sample(range(self.n), 3)
        fitnessMax = -1e9
        indexMax = -1
        for i in indexSample:
            if self.fitness[i] > fitnessMax:
                fitnessMax = self.fitness[i]
                indexMax = i
        return self.population[indexMax]
    
    # 選択する関数
    def _Selection(self):
        # return self._RouletteSelection()
        return self._TournamentSelection()
    
    # エリート選択
    # 一番適応値が高い個体はそのまま残す。
    def _Elite(self):
        fitnessMax = -1e9
        index = -1
        for i, fit in enumerate(self.fitness):
            if fit > fitnessMax:
                fitnessMax = fit 
                index = i
        return self.population[index]

    def _NextGeneration(self):

        # 適応度の計算
        self._CalcFitness()

        # エリート選択
        nextGeneration = [self._Elite()]

        while len(nextGeneration) < self.n:
            prob = random.random()
            if prob <= self.probCrossOver:
                individual1 = self._Selection()
                individual2 = self._Selection()
                newIndividual1, newIndividual2 = individual1.crossOver(individual2)
                nextGeneration.append(newIndividual1)
                nextGeneration.append(newIndividual2)
            elif prob <= self.probCrossOver + self.probCopy:
                newIndividual = self._Selection()
                nextGeneration.append(newIndividual)
            else:
                individual = self._Selection()
                newIndividual = individual.mutation()
                nextGeneration.append(newIndividual)

        return nextGeneration
        
    def Optimize(self):

        for _ in range(self.g):
            self.population = self._NextGeneration()
            print(f"elite = {self.population[0]}")

        return self._Elite()
        

class TetrisEval(Chromosome):
    def __init__(self, 
                 eval_height, 
                 eval_roughness, 
                 eval_blank_under_block,
                 eval_single,
                 eval_double,
                 eval_triple,
                 eval_tetris,
                 eval_t_spin_single,
                 eval_t_spin_double,
                 eval_t_spin_triple,
                 eval_t_spin_mini_single,
                 eval_t_spin_mini_double ):
        self.eval_height = eval_height 
        self.eval_roughness = eval_roughness
        self.eval_blank_under_block = eval_blank_under_block
        self.eval_single = eval_single
        self.eval_double = eval_double 
        self.eval_triple = eval_triple 
        self.eval_tetris = eval_tetris 
        self.eval_t_spin_single = eval_t_spin_single
        self.eval_t_spin_double = eval_t_spin_double 
        self.eval_t_spin_triple = eval_t_spin_triple 
        self.eval_t_spin_mini_single = eval_t_spin_mini_single
        self.eval_t_spin_mini_double = eval_t_spin_mini_double

    def randomGen(cls):
        return cls(
            random.randint(0, 1000),
            random.randint(0, 1000),
            random.randint(0, 1000),
            random.randint(0, 1000),
            random.randint(0, 1000),
            random.randint(0, 1000),
            random.randint(0, 1000),
            random.randint(0, 1000),
            random.randint(0, 1000),
            random.randint(0, 1000),
            random.randint(0, 1000),
            random.randint(0, 1000)
        )
        

    def fitness(self):
        global EVAL_LINE_CLEAR
        global EVAL_HEIGHT, EVAL_ROUGHNESS, EVAL_BLANK_UNDER_BLOCK
        global EVAL_T_SPIN_SINGLE, EVAL_T_SPIN_DOUBLE, EVAL_T_SPIN_TRIPLE
        global EVAL_T_SPIN_MINI_SINGLE, EVAL_T_SPIN_MINI_DOUBLE
        EVAL_LINE_CLEAR[0] = 0
        EVAL_LINE_CLEAR[1] = self.eval_single
        EVAL_LINE_CLEAR[2] = self.eval_double
        EVAL_LINE_CLEAR[3] = self.eval_triple
        EVAL_LINE_CLEAR[4] = self.eval_tetris
        EVAL_HEIGHT = self.eval_height
        EVAL_ROUGHNESS = self.eval_roughness
        EVAL_BLANK_UNDER_BLOCK = self.eval_blank_under_block
        EVAL_T_SPIN_SINGLE = self.eval_t_spin_single
        EVAL_T_SPIN_DOUBLE = self.eval_t_spin_double
        EVAL_T_SPIN_TRIPLE = self.eval_t_spin_triple
        EVAL_T_SPIN_MINI_SINGLE = self.eval_t_spin_mini_single
        EVAL_T_SPIN_MINI_DOUBLE = self.eval_t_spin_mini_double
        # todo implementation

    
    def crossOver(self, other):
        eval_height             = self.eval_height if random.random() < 0.5 else other.eval_height
        eval_roughness          = self.eval_roughness if random.random() < 0.5 else other.eval_roughness
        eval_blank_under_block  = self.eval_blank_under_block if random.random() < 0.5 else other.eval_blank_under_block
        eval_single             = self.eval_single if random.ranndom() < 0.5 else other.eval_single
        eval_double             = self.eval_double if random.random() < 0.5 else other.eval_double
        eval_triple             = self.eval_triple if random.random() < 0.5 else other.eval_triple
        eval_tetris             = self.eval_tetris if random.random() < 0.5 else other.eval_tetris
        eval_t_spin_single      = self.eval_t_spin_single if random.random() < 0.5 else other.eval_t_spin_single
        eval_t_spin_double      = self.eval_t_spin_double if random.random() < 0.5 else other.eval_t_spin_double
        eval_t_spin_triple      = self.eval_t_spin_triple if random.random() < 0.5 else other.eval_t_spin_triple
        eval_t_spin_mini_single = self.eval_t_spin_mini_single if random.random() < 0.5 else other.eval_t_spin_mini_single
        eval_t_spin_mini_double = self.eval_t_spin_mini_double if random.random() < 0.5 else other.eval_t_spin_mini_double
        return TetrisEval(
            eval_height, 
            eval_roughness, 
            eval_blank_under_block,
            eval_single,
            eval_double,
            eval_triple,
            eval_tetris,
            eval_t_spin_single,
            eval_t_spin_double,
            eval_t_spin_triple,
            eval_t_spin_mini_single,
            eval_t_spin_mini_double 
        )

    def mutation(self):
        eval_height             = self.eval_height if random.random() < 0.5 else self.eval_height + random.randint(-100,100)
        eval_roughness          = self.eval_roughness if random.random() < 0.5 else self.eval_roughness + random.randint(-100,100)
        eval_blank_under_block  = self.eval_blank_under_block if random.random() < 0.5 else self.eval_blank_under_block + random.randint(-100,100)
        eval_single             = self.eval_single if random.ranndom() < 0.5 else self.eval_single + random.randint(-100,100)
        eval_double             = self.eval_double if random.random() < 0.5 else self.eval_double + random.randint(-100,100)
        eval_triple             = self.eval_triple if random.random() < 0.5 else self.eval_triple + random.randint(-100,100)
        eval_tetris             = self.eval_tetris if random.random() < 0.5 else self.eval_tetris + random.randint(-100,100)
        eval_t_spin_single      = self.eval_t_spin_single if random.random() < 0.5 else self.eval_t_spin_single + random.randint(-100,100)
        eval_t_spin_double      = self.eval_t_spin_double if random.random() < 0.5 else self.eval_t_spin_double + random.randint(-100,100)
        eval_t_spin_triple      = self.eval_t_spin_triple if random.random() < 0.5 else self.eval_t_spin_triple + random.randint(-100,100)
        eval_t_spin_mini_single = self.eval_t_spin_mini_single if random.random() < 0.5 else self.eval_t_spin_mini_single + random.randint(-100,100)
        eval_t_spin_mini_double = self.eval_t_spin_mini_double if random.random() < 0.5 else self.eval_t_spin_mini_double + random.randint(-100,100)
        return TetrisEval(
            eval_height, 
            eval_roughness, 
            eval_blank_under_block,
            eval_single,
            eval_double,
            eval_triple,
            eval_tetris,
            eval_t_spin_single,
            eval_t_spin_double,
            eval_t_spin_triple,
            eval_t_spin_mini_single,
            eval_t_spin_mini_double 
        )

    def __str__(self):
        tostr = f"EVAL_HEIGHT = {self.eval_height}" \
                f"EVAL_RUGHNESS = {self.eval_roughness}" \
                f"EVAL_BLANK_UNDER_BLOCK = {self.eval_blank_under_block}" \
                f"EVAL_SINGLE = {self.eval_single}" \
                f"EVAL_DOUBLE = {self.eval_double}" \
                f"EVAL_TRIPLE = {self.eval_triple}" \
                f"EVAL_TETRIS = {self.eval_tetris}" \
                f"EVAL_T_SPIN_SINGLE = {self.eval_t_spin_single}" \
                f"EVAL_T_SPIN_DOUBLE = {self.eval_t_spin_double}" \
                f"EVAL_T_SPIN_TRIPLE = {self.eval_t_spin_triple}" \
                f"EVAL_T_SPIN_TETRIS = {self.eval_t_spin_tetris}" \
                f"EVAL_T_SPIN_MINI_SINGLE = {self.eval_t_spin_mini_single}" \
                f"EVAL_T_SPIN_MINI_DOUBLE = {self.eval_t_spin_mini_double}"
        
        return tostr

    