"""
Filename: MetaGPT/examples/debate.py
Created Date: Tuesday, September 19th 2023, 6:52:25 pm
Author: garylin2099
@Modified By: mashenquan, 2023-11-1. In accordance with Chapter 2.1.3 of RFC 116, modify the data type of the `send_to`
        value of the `Message` object; modify the argument type of `get_by_actions`.
"""

import asyncio
import platform
from typing import Any

import fire

from metagpt.actions import Action, UserRequirement
from metagpt.logs import logger
from metagpt.roles import Role
from metagpt.schema import Message
from metagpt.team import Team


class SpeakAloud(Action):
    """行为：在辩论（争吵）中大声发言"""

    PROMPT_TEMPLATE: str = """
    ## 背景
    你正在辩论，你带有强烈的偏见主张{profile}, 请关于{idea}展开辩论。
    ## 辩论历史    
    {context}
    ## 你的回合
    现在轮到你了，你应该攻击对手的论点，跳过已经说过的内容，禁止使用辩论历史里面的内容, 用80个词以内
    以{name}的修辞和观点，你的论点将是：
    """
    name: str = "SpeakAloud"

    async def run(self, context: str, name: str, profile:str, opponent_name: str, idea: str):
        #print(self)
        prompt = self.PROMPT_TEMPLATE.format(context=context, name=name, profile=profile, opponent_name=opponent_name, idea = idea)
        logger.info("prompt: "+prompt)

        rsp = await self._aask(prompt)

        logger.info("rsp: "+rsp)

        return rsp


class Debator(Role):
    name: str = ""
    profile: str = ""
    opponent_name: str = ""
    idea: str = ""

    def __init__(self, **data: Any):
        super().__init__(**data)
        self.set_actions([SpeakAloud])
        self._watch([UserRequirement, SpeakAloud])

    async def _observe(self) -> int:
        await super()._observe()
        # accept messages sent (from opponent) to self, disregard own messages from the last round
        self.rc.news = [msg for msg in self.rc.news if msg.send_to == {self.name}]
        return len(self.rc.news)

    async def _act(self) -> Message:
        logger.info(f"{self._setting}: to do {self.rc.todo}({self.rc.todo.name})")
        todo = self.rc.todo  # An instance of SpeakAloud

        memories = self.get_memories()
        context = "\n".join(f"{msg.sent_from}: {msg.content}" for msg in memories)
        # print(context)

        rsp = await todo.run(context=context, name=self.name, profile=self.profile ,opponent_name=self.opponent_name, idea=self.idea)

        msg = Message(
            content=rsp,
            role=self.profile,
            cause_by=type(todo),
            sent_from=self.name,
            send_to=self.opponent_name,
        )
        self.rc.memory.add(msg)

        return msg


async def debate(idea: str, investment: float = 3.0, n_round: int = 2):
    """Run a team of presidents and watch they quarrel. :)"""
    zhangsan = Debator(name="张三", profile="大男子主义", opponent_name="李四", idea="男人不应该做家务")
    lisi = Debator(name="李四", profile="女权主义", opponent_name="张三", idea="男人应该做家务")
    team = Team()
    team.hire([zhangsan, lisi])
    team.invest(investment)
    team.run_project(idea, send_to="张三")  # send debate topic to zhangsan and let him speak first
    await team.run(n_round=n_round)


def main(idea: str = "", investment: float = 3.0, n_round: int = 5):
    """
    :param idea: Debate topic, such as "Topic: The U.S. should commit more in climate change fighting"
                 or "lisi: Climate change is a hoax"
    :param investment: contribute a certain dollar amount to watch the debate
    :param n_round: maximum rounds of the debate
    :return:
    """
    if platform.system() == "Windows":
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(debate(idea, investment, n_round))


if __name__ == "__main__":
    fire.Fire(main)  # run as python debate.py --idea="TOPIC" --investment=3.0 --n_round=5
