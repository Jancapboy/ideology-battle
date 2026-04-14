# DEV_SPEC — 概念大逃杀 (Ideology Battle Royale)

## 1. 技术栈

| 层级 | 选择 | 理由 |
|------|------|------|
| 语言 | Python 3.11+ | 快速原型、丰富的类型支持 |
| 构建 | hatchling | 与 policy-dynamics-sim 保持一致 |
| 测试 | pytest + pytest-cov | 单元 + 集成测试 |
| 代码质量 | ruff + black + mypy | 与现有项目保持一致 |
| CI | GitHub Actions |  lint → unit → integration 三阶段 |
| 终端渲染 | rich / textual (可选) | 彩色日志、ASCII 战场 |

---

## 2. 目录结构

```
ideology-battle/
├── src/
│   └── ideology_battle/
│       ├── __init__.py
│       ├── core/
│       │   ├── __init__.py
│       │   ├── unit.py          # Unit 数据模型
│       │   ├── skill.py         # Skill 定义与效果系统
│       │   ├── buff.py          # Buff/Debuff 状态
│       │   ├── faction.py       # 阵营/羁绊定义
│       │   └── constants.py     # 网格大小、回合上限等常量
│       ├── engine/
│       │   ├── __init__.py
│       │   ├── battle_engine.py # 战斗核心引擎
│       │   ├── ai_controller.py # AI 寻敌与决策
│       │   └── shop_engine.py   # 商店/合成/经济逻辑
│       ├── data/
│       │   ├── __init__.py
│       │   ├── units.json       # 30 个概念的静态数据
│       │   ├── factions.json    # 阵营羁绊数据
│       │   └── items.json       # 装备数据
│       ├── cli/
│       │   ├── __init__.py
│       │   └── main.py          # 命令行入口
│       └── utils/
│           ├── __init__.py
│           └── replay.py        # 战斗回放序列化/反序列化
├── tests/
│   ├── unit/
│   │   ├── test_unit.py
│   │   ├── test_skill.py
│   │   ├── test_battle_engine.py
│   │   └── test_ai_controller.py
│   ├── integration/
│   │   └── test_battle_e2e.py  # 完整对战流程测试
│   └── conftest.py             # pytest fixtures
├── .github/
│   └── workflows/
│       └── ci.yml
├── pyproject.toml
├── README.md
├── PRD.md
└── DEV_SPEC.md
```

---

## 3. 接口约定

### 3.1 Unit 模型

```python
@dataclass
class Unit:
    id: str
    name: str
    faction_tags: list[str]
    hp: float
    max_hp: float
    atk: float
    spd: float
    skill: Skill | None = None
    items: list[Item] = field(default_factory=list)
    position: Position | None = None
    level: int = 1  # 1-3 星
```

### 3.2 Skill 接口

```python
class Skill(ABC):
    name: str
    cooldown: int  # 回合数
    trigger: TriggerType  # ACTIVE / PASSIVE / ON_DEATH / ON_KILL

    @abstractmethod
    def apply(self, caster: Unit, battle_state: BattleState) -> list[Event]:
        ...
```

### 3.3 BattleState

```python
@dataclass
class BattleState:
    grid: Grid
    units: list[Unit]
    turn: int
    events: list[Event]
    log: BattleLog
```

### 3.4 AI 决策接口

```python
def decide_action(unit: Unit, state: BattleState) -> Action:
    """返回一个 Action：MOVE / ATTACK / CAST / IDLE"""
    ...
```

---

## 4. 数据文件规范

### 4.1 units.json

```json
{
  "capitalism": {
    "name": "资本主义",
    "faction_tags": ["经济系"],
    "base_hp": 100,
    "base_atk": 15,
    "base_spd": 1.0,
    "skill_id": "invisible_hand"
  }
}
```

### 4.2 factions.json

```json
{
  "经济系": {
    "thresholds": [2, 4, 6],
    "effects": [
      {"type": "gold_bonus", "value": 0.2},
      {"type": "gold_bonus", "value": 0.5},
      {"type": "gold_bonus", "value": 1.0}
    ]
  }
}
```

---

## 5. 测试策略

### 5.1 单元测试（tests/unit/）

| 文件 | 覆盖内容 |
|------|---------|
| `test_unit.py` | Unit 初始化、升级、属性计算 |
| `test_skill.py` | 各技能的 apply 逻辑、事件生成 |
| `test_battle_engine.py` | 回合推进、伤害计算、死亡判定、胜利条件 |
| `test_ai_controller.py` | 寻敌范围、移动路径、目标选择优先级 |

### 5.2 集成测试（tests/integration/）

| 文件 | 覆盖内容 |
|------|---------|
| `test_battle_e2e.py` | 加载 2 个阵容 → 运行完整战斗 → 验证有且仅有 1 方获胜 → 验证回放可序列化/反序列化 |

### 5.3 覆盖率要求

- 单元测试：核心引擎代码 ≥ 80%
- 集成测试：覆盖 CLI 入口和完整对战流程

---

## 6. CI 配置

三阶段并行/串行：

```yaml
jobs:
  lint-and-type:
    ...
  unit-tests:
    matrix: [3.10, 3.11, 3.12]
    ...
  integration-tests:
    needs: unit-tests
    matrix: [3.10, 3.11, 3.12]
    ...
```

---

## 7. 开发里程碑

| 阶段 | 目标 | 预计工时 |
|------|------|---------|
| M0 | 搭项目骨架、CI 跑通 | 1h |
| M1 | Unit + Skill + BattleEngine 核心循环 | 3h |
| M2 | AI 寻敌 + 羁绊系统 + 10 个概念数据 | 3h |
| M3 | CLI 可视化 + 30 个概念 + 装备系统 | 3h |
| M4 | 集成测试 + 蒙特卡洛平衡测试脚本 | 2h |
| M5 | 回放系统 + README 文档 | 2h |

**MVP 总预计**：约 14 小时

---

## 8. 命名规范

- 模块/文件：`snake_case.py`
- 类：`PascalCase`
- 函数/变量：`snake_case`
- 常量：`SCREAMING_SNAKE_CASE`
- JSON key：`snake_case`
- 中文概念 ID：`pinyin_snake_case`（如 `tang_ping`、`nei_juan`）

---

## 9. 禁止事项

- 不允许硬编码技能逻辑在 BattleEngine 里，所有技能必须走 `Skill.apply()`
- 不允许直接修改 `Unit.hp` 绕过事件系统，所有状态变更必须生成 `Event`
- 不允许在核心引擎里引入阻塞 I/O（如 CLI 渲染必须在 engine 外做）
