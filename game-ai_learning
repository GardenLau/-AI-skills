#!/usr/bin/env python3
"""
游戏开发人机协同学习路径规划器

生成针对游戏工程的结构化学习路径，支持：前置确诊、动态直达、性能/管线演练。
"""

import argparse
import json
import os
import re
from datetime import datetime
from pathlib import Path

SKILL_NAME = "game-dev-learning-path-planner"

BROAD_SCOPE_PATTERN = re.compile(
    r"(?i)MMORPG|M\s*M\s*O|大型多人在线|元宇宙|开放世界\s*RPG|我想开发.*(MMO|端游大服)",
    re.IGNORECASE,
)


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="生成游戏工程人机协同学习路径（Markdown）")
    p.add_argument("--input-text", default="", help="原始自然语言，可含身份/对象/目标")
    p.add_argument("--identity", default="", help="身份定位（如客户端程序、TA、关卡）")
    p.add_argument("--learning-object", default="", help="学习对象（如 UE5 动作战斗、Addressables）")
    p.add_argument("--goal", default="", help="最终目标")
    p.add_argument("--engine", default="", help="引擎或栈（Unity/UE5/Godot 等）")
    p.add_argument("--stage", choices=["1", "2", "3"], default="", help="直达阶段 1/2/3")
    p.add_argument(
        "--direct-request",
        default="",
        help="直达交付说明（如第二阶段 Shader 效能审查 Checklist，Unity 环境）",
    )
    p.add_argument(
        "--need-practice",
        action="store_true",
        help="需用户明确授权后使用：输出含硬伤的代码/结构模拟供纠错",
    )
    p.add_argument("--output-file", default="", help="可选自定义输出文件路径")
    return p.parse_args()


def extract_labeled(text: str) -> dict:
    out = {"identity": "", "learning_object": "", "goal": "", "engine": ""}
    if not text:
        return out
    patterns = {
        "identity": r"(?:身份|角色)\s*[:：]\s*([^\n；;]+)",
        "learning_object": r"(?:对象|学习对象|模块)\s*[:：]\s*([^\n；;]+)",
        "goal": r"(?:目标|最终目标)\s*[:：]\s*([^\n；;]+)",
        "engine": r"(?:引擎|技术栈|环境)\s*[:：]\s*([^\n；;]+)",
    }
    for k, pat in patterns.items():
        m = re.search(pat, text, re.IGNORECASE)
        if m:
            out[k] = m.group(1).strip()
    if not out["engine"]:
        m = re.search(
            r"(?:Unity|UE4|UE5|Unreal|Godot|Cocos|自研引擎)",
            text,
            re.IGNORECASE,
        )
        if m:
            out["engine"] = m.group(0)
    return out


def merge_inputs(args: argparse.Namespace) -> dict:
    ext = extract_labeled(args.input_text)
    return {
        "identity": (args.identity or ext["identity"] or "").strip(),
        "learning_object": (args.learning_object or ext["learning_object"] or "").strip(),
        "goal": (args.goal or ext["goal"] or "").strip(),
        "engine": (args.engine or ext["engine"] or "").strip(),
    }


def is_vague(identity: str, learning_object: str, goal: str) -> bool:
    if sum(1 for x in (identity, learning_object, goal) if x) < 2:
        return True
    return False


def is_broad_unscoped(learning_object: str, goal: str, text: str) -> bool:
    combined = f"{learning_object} {goal} {text}"
    if not BROAD_SCOPE_PATTERN.search(combined):
        return False
    has_stack = bool(re.search(r"Unity|UE\d|Unreal|Godot|Cocos", combined, re.I))
    has_subsystem = bool(
        re.search(
            r"背包|战斗|寻路|同步|状态机|资源|热更|Addressables|联机|副本|"
            r"网络|反作弊|寻路|技能|UGUI|UI|Shader",
            combined,
        )
    )
    return not (has_stack and has_subsystem)


def section_clarify_vague() -> str:
    return """## 意图不明：请先一次性补充（追问）

当前无法可靠判断你的具体工程学习场景，**暂不生成学习路径**、**不调用工具猜测参数**。
请在**同一条回复**中补全下列 **3 项**（钉钉交互：一次列清）：

1. **领域分流**：**A）游戏开发工程** 还是 **B）非游戏通用**学习？若选 B，请改用「AI协同学习路径规划器」或在此明确「非游戏」并给出身份/对象/目标。
2. **身份 + 技术栈/平台**：岗位（客户端/服务端/TA 等）+ 引擎或语言（Unity/UE5/Go 等）+ 目标平台（PC/移动/主机）。
3. **子系统 + 盲区**：要落地的一个具体模块（如战斗状态机、Addressables、装扮后端）+ 当前能力短板（1～2 点）。
"""


def section_clarify_broad() -> str:
    return """## 前置确诊：项目范畴需收敛

检测到项目/目标维度过大（例如完整 MMORPG 级愿景）。在生成路径前请先明确：

- **技术栈二选一或组合**：Unity / UE5 / Godot 中你计划采用的主引擎与主语言。
- **能力盲区与里程碑**：在 0→1 的周期内，你准备先攻克的**一个**可交付子系统（如：背包+同步校验 / 单关卡战斗循环 / 资源热更管线）。
- **非目标声明**：本阶段**明确不做的**范围（如：不做全服同屏千人，暂不做全地图无缝）。

收到上述信息后再重新请求生成路径。
"""


def section_matrix(identity: str, learning_object: str, goal: str, engine: str) -> str:
    return f"""## 1) 工程解构与工具链映射

### 协同管线界分矩阵

| 模块 | AI工具执行域 | 人类主体域 | 建议工具链（示例） | 游戏语境下局限 |
| --- | --- | --- | --- | --- |
| 代码与脚本 | 模板类/接口骨架、单测桩、批注翻译、重命名与格式 | **ECS/核心系统架构**、**内存与生命周期**、**帧率预算**、多线程与锁序、**手感（Game Feel）** 调参裁决 | 代码助手（如 Cursor / Copilot）+ 版本差异对照 | 易引用**已弃用 API**、忽略引擎生命周期与**GC 压力** |
|  Shader / 材质 | 初版 HLSL/ShaderGraph、变体草图、命名规范提示 | 变体爆炸控制、**SRP Batcher/批处理**约束、真机热降频下表现 | 多模态+代码 LLM、引擎官方文档 | 无平台 GPU 真机数据时，易给**过度采样**与全精度运算 |
| 资源与内容 | 占位图、LODs 初稿、批量命名、**本地化**初翻 | **Addressables/流式**策略、**内存预算**、Art 与 Tech 的验收线 | 生成式美术工具 + 脚本辅助 | 无法替你做**资产生命周期**与**构建管线**的签核 |
| 玩法与体验 | 规则表草稿、状态穷举、**手感**调参表模板 | **Game Feel** 裁决、关键帧、输入到响应链路的责任归属 | 设计文档 LLM 辅助 | 无法替代**试玩-迭代**的实证闭环 |
| 性能与品质 | 静态扫描建议、**Profiler** 截图解读要点清单 | 帧时间预算、**DrawCall/批处理**、内存泄漏**根因** | 与引擎 Profiler 强绑定的人工复核 | 分析结论若脱离**具体帧/具体场景**则不可执行 |

### 推荐 AI 工具组合与适用域

| 用途 | 建议工具 | 游戏语境下技术局限 |
| --- | --- | --- |
| 逻辑推演、多步拆解、规格化清单 | Claude 3.5 Sonnet 等长上下文推理模型 | 仍可能输出与项目 **Package/引擎小版本** 不一致的 API 签名 |
| 代码补全、局部重构、工程内导航 | Cursor、GitHub Copilot | 对 **热路径分配、合批、物理步长** 的结论须用 **Profiler / Frame Debugger** 复核 |
| 美术意向、概念与占位资产 | Midjourney、Stable Diffusion | 不绑定 **显存/带宽/材质变体** 预算；需人类做 **LOD/压缩/合批** 签核 |

**当前输入摘要**
- 身份：{identity or "待补充"}
- 引擎/环境：{engine or "待补充"}
- 学习对象：{learning_object or "待补充"}
- 目标：{goal or "待补充"}
"""


def section_stage1(learning_object: str, engine: str) -> str:
    return f"""## 2) 进化式学习路径架构

### 阶段一（了解）

#### 系统级提问母版（Meta-Prompt）

1. 请把「{learning_object or "目标模块"}」在 {engine or "目标引擎"} 中拆为：数据模型、时序（Tick/Fixed/物理步）、**外部依赖**（Input/网络/资源）、**验收指标**（帧时、GC.Alloc/帧、加载时延）。
2. 指出哪些结论必须由人类定义（**预算/手感/防作弊**），哪些允许 AI 生成初稿后由人类删改。

#### 引擎核心底层术语 / API 图谱对照表

| 术语/机制 | 在引擎中的含义 | 与性能/正确性关联 | 易混点 |
| --- | --- | --- | --- |
| **主循环/帧** | 每帧 `Update` 与 **渲染提交** 的时序 | 把重逻辑放进每帧 = **CPU 帧时**与 **GC** 风险 | 与 **FixedUpdate/物理子步** 混用导致非确定性 |
| **物理子步/Fixed 步长** | 固定或可变步进下的物理/动画同步 | 步长与网络同步/回放紧密相关；错误步长导致穿模/抖动 | 与**渲染帧率**解耦 |
| **批处理/合批** | 减少 **DrawCall** 与**材质变体** | 材质实例参数不当可致 **SRP Batcher** 合批**失效** | 与 **Instance**、**合图集** 策略冲突 |
| **资源生命周期** | 加载/卸载/引用计数的时序 | 漏卸载 → **常驻内存**；早卸载 → 运行时**空引用** | **Addressables/Streaming** 与场景切换顺序 |
| **垃圾回收 (GC)** | 托管堆分配与回收 | 每帧 `new`/装箱/LINQ 可产生 **GC.Alloc** 峰值与卡顿 | 与 **struct/对象池** 取舍 |
"""


def section_stage2(learning_object: str, engine: str) -> str:
    return f"""### 阶段二（熟悉）

#### AI 在游戏工程中的典型幻觉靶向

- **已废弃/版本错配 API**：例如文档版本与项目 **Package** 或 **.NET/Mono** 版本不一致时仍给旧签名。
- **忽视 GC 与热路径分配**：在 **Update/网络回调** 中生成临时集合或字符串，产生可测的 **每帧分配**（应用 **Profiler/Deep Profile** 验证）。
- **无证据的性能断言**：仅称「可能慢」而不绑定 **某 Scene 的某实体数** 与 **合批/变体** 数据。

#### 代码与资产规范 / 效能缺陷审查清单

| 检查项 | 可观测失败样态（引擎侧） | 最小验证 | 不通过时处置 |
| --- | --- | --- | --- |
| 热路径分配 | `Profiler` 中 **GC.Alloc/帧** 在 `Update` 内尖峰 | 用 **深度采样** 定位到**具体调用** | 用对象池/`Span`/缓存字符串消除分配 |
| 合批/变体 | **Frame Debugger** 显示**材质变体/关键字**过碎 | 统计**材质实例数/Keyword** 与**SRP Batcher/批处理** 状态 | 合并 Keyword、用 **MaterialPropertyBlock** 等策略 |
| 物理与帧耦合 | 物理抖动与**渲染帧**强行同步 | 核对 **Fixed Timestep**、**Interpolation** 设置 | 明确「模拟步长 vs 表现插值」职责 |
| 死锁/锁序 | 两锁 **AB-BA** 取锁顺序在加载/热更路径中交叉 | 静态审查锁对象与 **主线程/工作线程** 模型 | 统一锁序，缩小临界区，避免在锁内**IO/资源** |
| 协程/异步与生命周期 | 对象销毁后仍**回调/等待** 继续访问 | 用 **取消令牌/引用弱绑定** 与场景卸载顺序验证 | 绑定 **所有权** 与 **取消** |

> 学习对象：{learning_object or "待定义"}；引擎语境：{engine or "待定义"}。
"""


def section_stage3(learning_object: str, engine: str) -> str:
    return f"""### 阶段三（掌握）

#### 边缘案例处理逻辑

1. **多人同步与回滚**：先声明 **权威源**（服务器/主客户端），再选择 **状态快照** 或 **插值+预测**；**回滚**必须绑定**输入帧序号**与**确定性**模拟边界。
2. **移动端热降频/发热**：将体验目标与 **可测量指标** 绑定，例如**目标帧、帧时间分布p95、Shader 指令数/带宽** 在**高温策略**下仍达标的阈值，而非“尽量优化”。

#### 全局架构、性能风险与设计干预原则

| 风险类型 | 具体机制举证（非泛化） | 干预原则 |
| --- | --- | --- |
| **主线程饥饿** | **每帧**在 `Update` 内对 `N>阈值` 对象做**完整遍历+LINQ** | 以 **O(1) 分桶/脏标记** 限制每帧工作集 |
| **Draw 路径断裂** | 同一材质**个别实例** 修改导致 **合批/Instancing 失效** | 统一**材质与关键字**，非必要不改 **per-instance 关键字** |
| **内存增长** | **静态字典** 持有已卸载关卡引用 → **无法 GC** 回收 | 生命周期 **WeakReference** 或**显式清理**+ **Profiler 内存**对比 |
| **死锁/倒置** | `lock(A){{ lock(B) }}` 与另一路径 `lock(B){{ lock(A) }}` 在**加载与音频**两线程交叉 | 禁止交叉锁，或 **单线程** 串行化资源 I/O |

> 学习对象：{learning_object or "待定义"}；引擎：{engine or "待定义"}。
"""


def section_guidance() -> str:
    return """## 3) 功能引导与演练触发

- 展开某一阶段请回复：`展开阶段1` / `展开阶段2` / `展开阶段3`（或在请求中直接 `--stage`）。
- 需某类 Checklist 请回复具体引擎与资产类型，如：`直接给我第二阶段，Unity 下 Addressables 资源加载与内存的审查清单`。
- 若需**潜藏性能硬伤的模拟代码或蓝图结构**用于纠错，请明确回复：`需要性能演练` / `需要审计演练` / `需要蓝图演练`（对应工具参数 `--need-practice`；未授权则不输出第 4 节）。
"""


def section_practice(learning_object: str, engine: str) -> str:
    eng = engine or "Unity C# 语境"
    return f"""## 4) 对抗性仿真演练（已获授权）

### 模拟半成品（含可定位硬伤，供你审查）

以下片段为**教学用**的刻意缺陷示例，目标场景：{learning_object or "未指定模块"}；环境：{eng}。

**片段 A：热路径与 GC**
```csharp
void Update() {{
    var list = new List<Enemy>(FindObjectsOfType<Enemy>());  // 每帧分配 + FindObjects* 高成本
    foreach (var e in list.Where(x => x.hp > 0))               // 潜在 LINQ/迭代器 分配
        e.Paint();
}}
```

**硬伤点（要求你在审查中标出并对应引擎机制）**
- 每帧 `new List` 与 `FindObjectsOfType` 对 **CPU 与 GC** 的复合伤害。
- `Where` 在部分情况下引入 **分配** 与**额外迭代**；应改为**缓存集合**+**可预测遍历**。

**片段 B：合批/材质（示意）**
- 在 **URP/内置** 中，为每个角色实例**每帧** `mat.EnableKeyword("FOO")` 且关键字组合不一致，可导致 **SRP Batcher/批处理** 在 **Frame Debugger** 中显示**合批被拆散**（需结合具体管线验证）。

**片段 C：蓝图结构（UE 语境示意，教学用缺陷）**
- 在 **Event Tick** 中每帧 **SpawnActor** 或每帧对全关卡 **GetAllActorsOfClass** 再遍历修改，等价于在 **Tick** 上叠加 **O(N)** 查询与**对象创建**；在 **stat unit / stat gpu** 与 **Unreal Insights** 中可表现为 **GameThread** 或 **RHI** 帧时尖峰。
- 在 **Construction Script** 中按随机种子**反复**修改 **StaticMesh** 缩放与材质参数，可导致**编辑器与 PIE 下**构建数据不一致，并放大 **HISM/ISM** 的重建成本（需用 **输出日志 + Insights** 对照验证）。

### 你的任务
1. 逐条标出**硬伤**并映射到**Profiler/Frame Debugger/内存**中的哪类证据。
2. 给出**可合并**的修改策略（不泛泛而谈“优化”）。
3. 提交你认可的**审查结论**与**未决项**（需真机/目标设备验证的项单独列出）。

### 参考纠偏（点评框架）
- **热路径是否零分配**：`Profiler` 中 **GC.Alloc** 行是否仍落在 `Update`。
- **查询成本是否摊销**：`Find*` 类 API 是否被**缓存/事件驱动** 替代。
- **渲染路径是否可证明**：`Frame Debugger` 是否仍显示**可接受的批/实例**。
- **UE 侧是否绑定 Tick 成本**：`stat unit` / **Insights** 中 **GameThread** 是否与 **Tick 内 Spawn / GetAll** 同相位尖峰。
"""


def infer_direct_request_from_text(text: str) -> str:
    """当自然语言含直达类触发词时，将整段作为直达指令（与 --direct-request 等价）。"""
    if not text or not text.strip():
        return ""
    triggers = ("跳过", "直达", "直接提取", "直接给", "直接生成", "给我生成")
    if any(t in text for t in triggers):
        return text.strip()
    return ""


def direct_section(direct: str, stage: str, learning_object: str, engine: str) -> str:
    head = ["## 直达交付"]
    if direct:
        head.append(f"- 用户指令：{direct}")
    if stage:
        head.append(f"- 目标阶段：阶段{stage}")
    head.append("")
    body: list[str] = []
    if stage == "1":
        body.append(section_stage1(learning_object, engine))
    elif stage == "2":
        body.append(section_stage2(learning_object, engine))
    elif stage == "3":
        body.append(section_stage3(learning_object, engine))
    else:
        d = direct or ""
        if any(x in d for x in ("第三", "阶段3")):
            body.append(section_stage3(learning_object, engine))
        elif any(x in d for x in ("第一", "阶段1")):
            body.append(section_stage1(learning_object, engine))
        elif any(x in d for x in ("第二", "阶段2")) or "checklist" in d.lower() or "审查" in d:
            body.append(section_stage2(learning_object, engine))
        else:
            body.append(section_stage2(learning_object, engine))
    body.append(section_guidance())
    return "\n".join(head + body)


def build_full(identity, learning_object, goal, engine, need_practice: bool) -> str:
    parts = [
        "# 游戏开发人机协同学习路径",
        section_matrix(identity, learning_object, goal, engine),
        section_stage1(learning_object, engine),
        section_stage2(learning_object, engine),
        section_stage3(learning_object, engine),
        section_guidance(),
    ]
    if need_practice:
        parts.append(section_practice(learning_object, engine))
    return "\n\n".join(parts)


def ensure_output_path(custom: str) -> Path:
    if custom:
        p = Path(custom)
        p.parent.mkdir(parents=True, exist_ok=True)
        return p
    staff_id = os.environ.get("TYCLAW_SENDER_STAFF_ID", "unknown")
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    d = Path(f"/tmp/tyclaw_{staff_id}_{ts}_{SKILL_NAME}/")
    d.mkdir(parents=True, exist_ok=True)
    return d / "game_dev_learning_path.md"


def main() -> int:
    args = parse_args()
    merged = merge_inputs(args)
    identity = merged["identity"]
    learning_object = merged["learning_object"]
    goal = merged["goal"]
    engine = merged["engine"]
    text = args.input_text

    direct_req = (args.direct_request or "").strip()
    if not direct_req:
        direct_req = infer_direct_request_from_text(text)

    if args.stage or direct_req:
        out = direct_section(
            direct_req,
            args.stage,
            learning_object,
            engine,
        )
        if args.need_practice:
            out = out + "\n\n" + section_practice(learning_object, engine)
    elif is_broad_unscoped(learning_object, goal, text):
        out = section_clarify_broad()
    elif is_vague(identity, learning_object, goal):
        out = section_clarify_vague()
    else:
        out = build_full(identity, learning_object, goal, engine, args.need_practice)

    path = ensure_output_path(args.output_file)
    path.write_text(out + "\n", encoding="utf-8")
    print(out)
    print("\n---")
    print(json.dumps({"output_file": str(path)}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
