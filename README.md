# Ideology Battle Royale

把抽象概念/意识形态变成自走棋单位，看它们在战场上互相厮杀。

## 安装

```bash
git clone https://github.com/Jancapboy/ideology-battle.git
cd ideology-battle
pip install -e ".[dev]"
```

## 玩法

### 运行主题对战（Demo）

```bash
ideology-battle demo
```

### 运行随机快速对战

```bash
ideology-battle quick
```

### 慢动作模式

```bash
ideology-battle demo --slow
```

## 测试

```bash
pytest tests/unit
pytest tests/integration
```

## 首批概念（15个）

资本主义、社会主义、躺平、内卷、人工智能、996、远程办公、算法推荐、消费主义、民主、区块链、元宇宙、老大哥、气候危机、取消文化

## CI 状态

[![CI](https://github.com/Jancapboy/ideology-battle/actions/workflows/ci.yml/badge.svg)](https://github.com/Jancapboy/ideology-battle/actions)
