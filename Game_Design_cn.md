### **多玩家模拟城市游戏设计方案**
---

## **游戏概述**

### **目标**
1. 玩家（智能体）需要在有限资源和动态环境中采取行动，通过建造不同类型的建筑优化自己的收益。
2. 每个玩家既追求个人利益（如金钱和声望），又需要兼顾全局环境得分以避免环境崩溃带来的负面影响。
3. 游戏设计旨在让智能体学习到合作能够在长期中提升整体分数，同时保留足够的利益竞争以保持复杂性和策略多样性。

---

## **游戏核心机制**


---

### **棋盘**
- **地图大小：** 4x4 网格。
- **初始状态：** 全空，每个格子可以建造不同类型的建筑。
- 
为每个地块引入以下三个核心指数，均以 [0, 100] 的相对值表示，初始值均为 30, 每回合根据地块间的关系动态更新棋盘上的每个格子的参数：

1. **绿地指数（Greenery Index, \( G \)）：**

2. **活力指数（Vitality Index, \( V \)）：**

3. **密度指数（Density Index, \( D \)）：**


### **信息不完全性**
1. **隐藏资源：**
   - 每名玩家的金钱和声望对其他玩家不可见。

### **资源限制**
- 每名玩家初始拥有 20 金钱和 20 声望。
- 当玩家的资源耗尽时，本回合只能选择跳过。


### 地块类型

### ** 公园（Park）**
- **价格**
  - 消耗 1 金钱
  - 消耗 3 声望
- **utility**
  - 每回合给建造玩家减少1金钱
  - 每回合给建造玩家增加3声望
- **好处**
  - 增加绿地指数：自身 \( G +30 \)，周边相邻格子 \( G +10 \)。
- **缺点**
  - 抑制商业活力：自身 \( V -30 \), 周边相邻格子 \( V -10 \)。

### ** 住宅（House）**
- **价格**
  - 消耗 2 金钱
  - 消耗 2 声望
- **utility**
  - 每回合给建造玩家增加2金钱
- **好处**
  - 增加密度指数：自身 \( D +30 \)，周边相邻格子 \( D +10 \)。
- **缺点**
  - 减少绿地指数：自身 \( G -30 \)，周边相邻格子 \( G -10 \)。

### ** 商店（Shop）**
- **价格**
  - 消耗 3 金钱
  - 消耗 1 声望
- **utility**
  - 每回合给建造玩家增加3金钱
  - 每回合给建造玩家减少1声望
- **好处**
  - 增加活力指数：自身 \( V +30 \)，周边相邻格子 \( V +10 \)。
- **缺点**
  - 降低住宅舒适度：自身 \( D -30 \), 周边相邻格子 \( D -10 \)。




### **玩家**
- 玩家人数：3 名（可扩展到更多玩家）。
- 每个玩家的特性：
  - **资源：** 每名玩家拥有独立的金钱和声望。
  - **收益函数：** 每名玩家根据其行动获取奖励，奖励分为 **个人收益** 和 **环境得分贡献**：
    \[
    u_i = \alpha \cdot \text{self\_score}_i + \beta \cdot \text{environment\_score}
    \]
    其中 \( \alpha, \beta \) 是玩家偏好的权重，每个玩家在游戏开始时分配不同的权重，形成策略差异化。
  - 每名玩家跟踪spend和earned, 用于后续评分

## **玩家设计**

### **玩家 A：经济型玩家（Economic Player）**
- **特性：** 专注于金钱收益，通过商店建设和高活力区域的开发获取短期回报。
- **收益函数：**
  \[
  \text{self\_score}_A = 0.8 \cdot \text{money\_earned} + 0.2 \cdot \text{reputation\_earned}
  \]


### **玩家 B：声望型玩家（Reputation Player）**
- **特性：** 专注于声望的提升，通过住宅和公园的协同建设建立高声望社区。
- **收益函数：**
  \[
  \text{self\_score}_B = 0.2 \cdot \text{money\_earned} + 0.8 \cdot \text{reputation\_earned}
  \]


### **玩家 C：平衡型玩家（Balanced Player）**
- **特性：** 同时关注金钱和声望，倾向于在经济和环境中寻找平衡点。
- **收益函数：**
  \[
  \text{self\_score}_C = 0.5 \cdot \text{money\_earned} + 0.5 \cdot \text{reputation\_earned}
  \]


### **玩家行动**
玩家按顺序行动, 每个玩家在其回合可以执行以下操作：
1. **建造建筑：** 消耗金钱和声望, 在棋盘的空格上建造建筑。

### **玩家策略** 

**平均策略 (Baseline)**
   - 平均选择动作
  
**短期收益最优化策略**
   - 选择对自己regret最小的策略


## 评分机制

环境得分 \( \text{Global Environment Score} \) 基于棋盘上所有格子的参数加权计算：
\[
\text{Global Environment Score} = w_G \cdot \bar{G} + w_V \cdot \bar{V} + w_D \cdot \bar{D}
\]

- \( \bar{G}, \bar{V}, \bar{D} \)：棋盘所有格子对应指数的平均值。
- \( w_G, w_V, w_D \)：权重，初始值为 \( w_G = 1/3, w_V = 1/3, w_D = 1/3 \)。


总体得分计算公式：
\[
\text{Final Score}_i = \alpha \cdot \text{self\_score}_i + \beta \cdot \text{environment\_score}
\]

Where: $\alpha = 0.5$ $\beta = 0.5$

### **结束条件**
棋盘被填满。

### **评估**
游戏结束后, 我们评估每个玩家对自己目标的贡献和对整体目标的贡献. 游戏没有赢家.

## **多智能体博弈设计**

### **学习目标**
1. **学习合作策略：**
   - 智能体需要平衡环境得分与个人得分，学习到在特定场景下合作。
2. **竞争与阻碍：**
   - 智能体可以选择竞争型策略，通过降低其他玩家的收益来提升自己的优势。


## **游戏动态与实验方向**
我们想计算出每名玩家的最佳stragety, 以及 Course correlated equalibrium

### **评估指标**
1. **合作度：** 玩家选择对环境有益行为的比例。
2. **收益分布：** 观察各玩家的最终分数分布。
3. **策略多样性：** 不同智能体策略之间的差异化。

---

## **游戏可视化**
用字符画形式表达游戏棋盘信息
以格式化文本方式输出 global environment score
以格式化文本方式输出 每个玩家目前的资源, 收益, 该回合选择的动作, self_score 与 intergrated_score
