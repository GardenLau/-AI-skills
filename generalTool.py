#!/usr/bin/env python3
"""
AI协同学习路径规划器

生成结构化学习路径，支持：
1. 前置确诊（输入模糊时先收敛问题）
2. 动态流程控制（直达指定阶段或资产）
3. 对抗性演练（需明确触发）
"""

import argparse
import json
import os
import re
from datetime import datetime
from pathlib import Path


SKILL_NAME = "ai-learning-path-planner"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="生成 AI 协同学习路径（Markdown）"
    )
    parser.add_argument(
        "--input-text",
        default="",
        help="用户原始输入文本，可包含“身份/对象/目标”",
    )
    parser.add_argument("--identity", default="", help="身份定位")
    parser.add_argument("--learning-object", default="", help="学习对象")
    parser.add_argument("--goal", default="", help="最终目标")
    parser.add_argument(
        "--stage",
        choices=["1", "2", "3"],
        default="",
        help="直达指定阶段（1/2/3）",
    )
    parser.add_argument(
        "--direct-request",
        default="",
        help="用户要求直接交付的资产说明（如：第二阶段Checklist）",
    )
    parser.add_argument(
        "--need-practice",
        action="store_true",
        help="是否直接输出对抗性仿真演练内容",
    )
    parser.add_argument(
        "--output-file",
        default="",
        help="可选：自定义输出文件路径",
    )
    return parser.parse_args()


def extract_labeled_fields(text: str) -> dict:
    fields = {"identity": "", "learning_object": "", "goal": ""}
    if not text:
        return fields

    patterns = {
        "identity": r"(?:身份|角色)\s*[:：]\s*([^\n；;]+)",
        "learning_object": r"(?:对象|学习对象)\s*[:：]\s*([^\n；;]+)",
        "goal": r"(?:目标|最终目标)\s*[:：]\s*([^\n；;]+)",
    }
    for key, pattern in patterns.items():
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            fields[key] = match.group(1).strip()
    return fields


def normalize_inputs(args: argparse.Namespace) -> dict:
    parsed = extract_labeled_fields(args.input_text)
    identity = args.identity.strip() or parsed["identity"]
    learning_object = args.learning_object.strip() or parsed["learning_object"]
    goal = args.goal.strip() or parsed["goal"]
    return {
        "identity": identity,
        "learning_object": learning_object,
        "goal": goal,
    }


def is_vague(identity: str, learning_object: str, goal: str) -> bool:
    populated = sum(1 for x in [identity, learning_object, goal] if x)
    return populated < 2


def build_clarifying_questions() -> str:
    return (
        "## 意图不明：请先一次性补充（追问）\n\n"
        "当前无法可靠判断你的具体学习场景，**暂不生成学习路径**、**不调用工具猜测参数**。"
        "请在**同一条回复**中补全下列 **3 项**（钉钉交互：一次列清）：\n\n"
        "1. **领域分流**：**A）通用职场/业务/合规等** 还是 **B）游戏开发工程**（客户端/服务端/TA/引擎/性能等）？"
        "若选 B，请写清引擎/语言与模块名，或改用「游戏开发人机协同学习路径规划器」触发。\n"
        "2. **身份 + 学习对象**：你的职责边界 + 要学的具体模块/名词（各一行即可）。\n"
        "3. **可验证目标**：你希望学完后能独立交付什么可验收结果？\n"
    )


def matrix_section(identity: str, learning_object: str, goal: str) -> str:
    return f"""## 1) 领域解构与工具链映射

### 跨界协同界分矩阵

| 模块 | AI工具执行域 | 人类主体域 | 推荐工具链 | 技术局限 |
|---|---|---|---|---|
| 信息抽取与归档 | 批量抽取条款、术语归并、结构化摘要 | 定义抽取口径与优先级 | 通用LLM + 规则模板 | 对隐含前提和语义冲突识别不稳定 |
| 初步方案生成 | 产出初稿框架、候选清单、比对版本 | 决定取舍标准与最终策略 | LLM + 表格化清单 | 容易生成“看似完整但证据不足”的内容 |
| 缺陷扫描 | 标注显性矛盾、格式异常、引用缺失 | 判断缺陷严重度与处置动作 | LLM + 规则校验 | 无法替代业务责任判断 |
| 决策与签发 | 提供备选建议与风险提示 | 最终责任归属、价值判断、合规兜底 | 人类主导 | AI不能承担责任主体角色 |

**当前目标场景**
- 身份：{identity or "待补充"}
- 学习对象：{learning_object or "待补充"}
- 目标：{goal or "待补充"}
"""


def stage_one_section(learning_object: str) -> str:
    return f"""## 2) 进化式学习路径架构

### 阶段一（了解）

#### 提问母版（Meta-Prompt）
1. 任务定义：请将「{learning_object or "目标业务"}」拆解为输入、约束、输出三层结构。
2. 边界声明：明确哪些结论必须由人类确认，哪些步骤允许AI自动化。
3. 证据要求：每一条判断都要附“依据来源+可核验证据位点”。

#### 领域核心术语对照表
| 术语 | 操作定义 | 常见误读 | 校验方式 |
|---|---|---|---|
| 事实 | 可被证据直接支撑的信息 | 把推断当事实 | 标注证据编号并复核来源 |
| 规则 | 可执行的判断标准 | 只记结论不记适用条件 | 列出适用范围与例外 |
| 风险 | 对目标造成负向影响的事件 | 把不确定性等同风险 | 给出触发条件与影响路径 |
"""


def stage_two_section(learning_object: str) -> str:
    return f"""### 阶段二（熟悉）

#### 幻觉靶向分析
- **高发点1：伪造依据**：模型给出不存在的法条、指标口径或接口行为。
- **高发点2：条件遗漏**：结论忽略适用前提，导致错误泛化。
- **高发点3：冲突未对齐**：同一输出内出现自相矛盾的规则。

#### 合规性与缺陷审查清单（Checklist）
| 检查项 | 失败样态 | 最小验证动作 | 处置原则 |
|---|---|---|---|
| 依据可追溯 | 引用来源不存在或不可定位 | 抽检3条关键结论的来源 | 任何一条不可追溯即退回重写 |
| 适用条件完整 | 结论未声明边界 | 逐条补“适用/不适用”条件 | 缺边界即禁止落地 |
| 逻辑一致性 | 前后规则冲突 | 建立“结论-证据-规则”三列对照 | 存在冲突时由人类裁决 |
| 风险分级可执行 | 只给抽象风险描述 | 要求风险等级+触发阈值 | 不可执行则不进入流程 |

> 适用对象：{learning_object or "待定义对象"}
"""


def stage_three_section(learning_object: str) -> str:
    return f"""### 阶段三（掌握）

#### 边缘案例处理逻辑
1. 先识别冲突类型：规则冲突、证据冲突、目标冲突。
2. 再定义仲裁顺序：强制性约束 > 业务目标 > 效率偏好。
3. 最后记录决策痕迹：保留“被否决方案+否决理由+责任人”。

#### 全局风险图谱与干预原则
| 风险节点 | 触发信号 | 干预动作 | 责任主体 |
|---|---|---|---|
| 输入污染 | 来源不明、字段缺失 | 回退到数据校验层重新清洗 | 人类 |
| 推理漂移 | 中间结论偏离任务目标 | 强制复用任务定义模板 | 人类+AI |
| 输出误导 | 结论可读但不可执行 | 增加执行阈值与审签门槛 | 人类 |

> 当前训练聚焦：{learning_object or "待定义对象"} 的高风险场景处理。
"""


def guidance_section() -> str:
    return """## 3) 功能引导与演练触发

- 若你要展开某一阶段，请直接回复：`展开阶段1` / `展开阶段2` / `展开阶段3`。
- 若你要直接拿交付物，请直接回复：`直接给我[资产名称]`。
- 若你要进行纠错训练，请明确回复：`需要演练`。
"""


def practice_section(learning_object: str) -> str:
    return f"""## 4) 对抗性仿真演练

### 模拟半成品（含硬伤）
场景：{learning_object or "合同审查"}

> “本合同不存在用工风险。根据《劳动合同法》第99条，试用期可设置为12个月。乙方若连续旷工1天，甲方可立即解除合同且无需补偿。”

### 任务要求
- 标出至少3处具体硬伤（条文、阈值、程序要件或证据链）。
- 给出逐条纠偏建议，并说明对应的业务后果。
- 输出修订版结论，必须包含适用边界。

### 参考点评框架
1. **法条准确性**：核查条文编号与适用范围。
2. **程序合法性**：审查解除条件与通知义务。
3. **风险后果**：评估争议成本与败诉暴露面。
"""


def direct_delivery_section(request: str, stage: str, learning_object: str) -> str:
    title = "## 直达交付"
    lines = [title]
    if request:
        lines.append(f"- 用户指令：{request}")
    if stage:
        lines.append(f"- 目标阶段：阶段{stage}")
    lines.append("")

    if stage == "1":
        lines.append(stage_one_section(learning_object))
    elif stage == "2":
        lines.append(stage_two_section(learning_object))
    elif stage == "3":
        lines.append(stage_three_section(learning_object))
    else:
        lowered = request.lower()
        if "第二" in request or "stage 2" in lowered or "checklist" in lowered:
            lines.append(stage_two_section(learning_object))
        elif "第一" in request or "stage 1" in lowered:
            lines.append(stage_one_section(learning_object))
        elif "第三" in request or "stage 3" in lowered:
            lines.append(stage_three_section(learning_object))
        else:
            lines.append(
                "未识别具体阶段，默认输出阶段二《合规性与缺陷审查清单》。\n\n"
                + stage_two_section(learning_object)
            )
    lines.append(guidance_section())
    return "\n".join(lines)


def build_markdown(
    identity: str,
    learning_object: str,
    goal: str,
    stage: str,
    direct_request: str,
    need_practice: bool,
) -> str:
    # 动态流程控制：用户要求直达时，不输出标准流程
    if stage or direct_request:
        content = direct_delivery_section(direct_request, stage, learning_object)
        if need_practice:
            content += "\n" + practice_section(learning_object)
        return content

    sections = [
        "# AI协同学习路径规划",
        matrix_section(identity, learning_object, goal),
        stage_one_section(learning_object),
        stage_two_section(learning_object),
        stage_three_section(learning_object),
        guidance_section(),
    ]

    if need_practice:
        sections.append(practice_section(learning_object))
    return "\n\n".join(sections)


def ensure_output_path(custom_output: str) -> Path:
    if custom_output:
        path = Path(custom_output)
        path.parent.mkdir(parents=True, exist_ok=True)
        return path

    staff_id = os.environ.get("TYCLAW_SENDER_STAFF_ID", "unknown")
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    output_dir = Path(f"/tmp/tyclaw_{staff_id}_{timestamp}_{SKILL_NAME}/")
    output_dir.mkdir(parents=True, exist_ok=True)
    return output_dir / "learning_path.md"


def main() -> int:
    args = parse_args()
    normalized = normalize_inputs(args)
    identity = normalized["identity"]
    learning_object = normalized["learning_object"]
    goal = normalized["goal"]

    if is_vague(identity, learning_object, goal) and not (args.stage or args.direct_request):
        markdown = build_clarifying_questions()
    else:
        markdown = build_markdown(
            identity=identity,
            learning_object=learning_object,
            goal=goal,
            stage=args.stage,
            direct_request=args.direct_request.strip(),
            need_practice=args.need_practice,
        )

    output_file = ensure_output_path(args.output_file)
    output_file.write_text(markdown + "\n", encoding="utf-8")

    print(markdown)
    print("\n---")
    print(json.dumps({"output_file": str(output_file)}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
