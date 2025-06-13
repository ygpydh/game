# 🕵️‍♂️ 炸弹迷宫小偷游戏 Thief Maze Bomb Game

![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)
![Pygame](https://img.shields.io/badge/Pygame-2.0+-green.svg)
![License](https://img.shields.io/badge/License-MIT-yellow.svg)

---

## 目录

- [游戏简介](#游戏简介)
- [玩法说明](#玩法说明)
- [项目结构](#项目结构)
- [运行指南](#运行指南)
- [未来规划](#未来规划)
- [贡献](#贡献)
- [致谢](#致谢)

---

## 游戏简介

炸弹迷宫小偷游戏是一款基于 Python 和 Pygame 的迷宫闯关游戏，  
玩家扮演小偷，在迷宫中收集宝藏，躲避守卫，用炸弹击晕守卫，最终逃脱迷宫！

---

## 玩法说明

| 操作          | 说明                       |
|---------------|----------------------------|
| 方向键        | 控制小偷移动               |
| 空格          | 放置炸弹                   |
| 收集宝藏(黄色) | 收集所有宝藏解锁出口       |
| 避开守卫(红色) | 守卫有视线，避免被发现     |
| 使用炸弹      | 炸晕守卫，赢得游戏         |

---

## 项目结构

```
thief-maze-game/
├── main.py          # 主程序入口
├── config.py        # 配置文件
├── maze.py          # 地图与绘制逻辑
├── player.py        # 玩家逻辑
├── guard.py         # 守卫逻辑
├── bomb.py          # 炸弹与爆炸逻辑
└── README.md        # 项目说明文件
```

---

## 运行指南

1. 安装 Python 3.x  
2. 安装 Pygame  
```bash
pip install pygame
```
3. 运行游戏  
```bash
python main.py
```

---

## 未来规划

- 多关卡迷宫随机生成  
- 多守卫AI及复杂巡逻路线  
- 丰富炸弹与道具系统  
- 音效及背景音乐支持  
- 保存进度与排行榜  

---

## 贡献

欢迎提交 Issue 或 Pull Request，  
一起来完善游戏！

---

## 致谢

感谢你的关注与支持，祝你游戏愉快！🎉
